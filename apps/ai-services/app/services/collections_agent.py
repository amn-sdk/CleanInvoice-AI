from typing import TypedDict, Literal, Optional
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import os

# Collection states
CollectionState = Literal[
    "NOT_DUE",
    "AT_DUE",
    "LATE_SOFT",
    "LATE_HARD",
    "NEGOTIATION",
    "CLOSED_PAID",
    "CLOSED_LOST"
]

class CollectionGraphState(TypedDict):
    """State for the collection agent graph."""
    invoice_id: str
    invoice_number: str
    amount: float
    customer_name: str
    customer_email: str
    days_overdue: int
    payment_history: str
    current_state: CollectionState
    next_action: str
    email_subject: str
    email_body: str
    strategy: str  # SOFT, STANDARD, AGGRESSIVE

class CollectionAgent:
    """AI agent for managing debt collection using LangGraph."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for collection agent")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Build the state machine graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for collections."""
        workflow = StateGraph(CollectionGraphState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_situation)
        workflow.add_node("generate_email", self._generate_email)
        workflow.add_node("escalate", self._escalate)
        workflow.add_node("close", self._close_case)
        
        # Define edges (transitions)
        workflow.set_entry_point("analyze")
        
        workflow.add_conditional_edges(
            "analyze",
            self._route_action,
            {
                "send_email": "generate_email",
                "escalate": "escalate",
                "close": "close",
                "wait": END
            }
        )
        
        workflow.add_edge("generate_email", END)
        workflow.add_edge("escalate", END)
        workflow.add_edge("close", END)
        
        return workflow.compile()
    
    def _analyze_situation(self, state: CollectionGraphState) -> CollectionGraphState:
        """Analyze the invoice situation and determine next action."""
        days = state["days_overdue"]
        strategy = state.get("strategy", "STANDARD")
        
        # Determine state based on days overdue
        if days < 0:
            new_state = "NOT_DUE"
        elif days == 0:
            new_state = "AT_DUE"
        elif days <= 7:
            new_state = "LATE_SOFT"
        elif days <= 30:
            new_state = "LATE_HARD"
        else:
            new_state = "NEGOTIATION"
        
        state["current_state"] = new_state
        return state
    
    def _route_action(self, state: CollectionGraphState) -> str:
        """Route to the appropriate action based on state."""
        current_state = state["current_state"]
        
        if current_state in ["CLOSED_PAID", "CLOSED_LOST"]:
            return "close"
        elif current_state == "NOT_DUE":
            return "wait"
        elif current_state == "NEGOTIATION" and state["days_overdue"] > 60:
            return "escalate"
        else:
            return "send_email"
    
    def _generate_email(self, state: CollectionGraphState) -> CollectionGraphState:
        """Generate personalized collection email using LLM."""
        current_state = state["current_state"]
        days = state["days_overdue"]
        amount = state["amount"]
        customer = state["customer_name"]
        invoice = state["invoice_number"]
        strategy = state.get("strategy", "STANDARD")
        
        # Determine tone based on state and strategy
        if current_state == "AT_DUE":
            tone = "friendly reminder"
        elif current_state == "LATE_SOFT":
            tone = "polite but firm"
        elif current_state == "LATE_HARD":
            tone = "serious and urgent"
        else:
            tone = "formal and escalated"
        
        if strategy == "SOFT":
            tone = f"very {tone.split(' and ')[0]} and understanding"
        elif strategy == "AGGRESSIVE":
            tone = f"{tone} with legal implications mentioned"
        
        # System prompt
        system_prompt = f"""You are a professional debt collection agent for CleanInvoice.
Your task is to write a {tone} email to collect payment for an overdue invoice.

Guidelines:
- Be professional and respectful
- Clearly state the invoice number and amount
- Mention the number of days overdue
- Suggest a clear action (payment or contact)
- Maintain a tone that is: {tone}
- Keep it concise (max 200 words)
- Sign as "L'équipe CleanInvoice"
"""
        
        # User prompt
        user_prompt = f"""Write a collection email for:
- Customer: {customer}
- Invoice: {invoice}
- Amount: {amount:.2f} €
- Days overdue: {days}
- Current state: {current_state}

Provide both subject and body."""
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        email_content = response.content
        
        # Parse subject and body
        lines = email_content.split('\n')
        subject = lines[0].replace("Subject:", "").replace("Objet:", "").strip()
        body = '\n'.join(lines[2:]).strip()  # Skip subject and empty line
        
        state["email_subject"] = subject
        state["email_body"] = body
        state["next_action"] = "email_sent"
        
        return state
    
    def _escalate(self, state: CollectionGraphState) -> CollectionGraphState:
        """Escalate to manual review or legal action."""
        state["next_action"] = "escalate_to_manager"
        state["email_subject"] = f"URGENT: Facture {state['invoice_number']} - Escalade nécessaire"
        state["email_body"] = f"""Cette facture nécessite une action immédiate.
        
Client: {state['customer_name']}
Montant: {state['amount']:.2f} €
Retard: {state['days_overdue']} jours

Action recommandée: Intervention manuelle ou procédure judiciaire."""
        
        return state
    
    def _close_case(self, state: CollectionGraphState) -> CollectionGraphState:
        """Close the collection case."""
        state["next_action"] = "case_closed"
        return state
    
    def process_invoice(self, invoice_data: dict) -> dict:
        """
        Process an invoice through the collection agent.
        
        Args:
            invoice_data: Dictionary with invoice information
            
        Returns:
            Dictionary with recommended action and generated email
        """
        # Initialize state
        initial_state: CollectionGraphState = {
            "invoice_id": invoice_data["id"],
            "invoice_number": invoice_data["number"],
            "amount": invoice_data["amount"],
            "customer_name": invoice_data["customer_name"],
            "customer_email": invoice_data.get("customer_email", ""),
            "days_overdue": invoice_data["days_overdue"],
            "payment_history": invoice_data.get("payment_history", "No history"),
            "current_state": "NOT_DUE",
            "next_action": "",
            "email_subject": "",
            "email_body": "",
            "strategy": invoice_data.get("strategy", "STANDARD")
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "invoice_id": result["invoice_id"],
            "state": result["current_state"],
            "action": result["next_action"],
            "email": {
                "subject": result["email_subject"],
                "body": result["email_body"],
                "to": result["customer_email"]
            }
        }
