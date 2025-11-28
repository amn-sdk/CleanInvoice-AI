# Instructions pour pousser sur GitHub

## Étapes à suivre :

### 1. Créer le repository sur GitHub

1. Va sur https://github.com/new
2. **Repository name**: `CleanInvoice-AI`
3. **Description**: `Modern invoice management platform with AI-powered features`
4. **Visibility**: Public ou Private (selon ta préférence)
5. ⚠️ **NE COCHE PAS** "Add a README file" ni ".gitignore" (on les a déjà)
6. Clique sur "Create repository"

### 2. Pousser le code

Une fois le repo créé, GitHub va te donner des commandes. Utilise celles-ci :

```bash
cd "/Users/aminesaddik/Documents/Amine/Projet Code /CleanInvoice"

# Ajouter le remote (remplace 'amn-sdk' par ton username si différent)
git remote add origin https://github.com/amn-sdk/CleanInvoice-AI.git

# Renommer la branche master en main (convention GitHub moderne)
git branch -M main

# Pousser la branche main
git push -u origin main

# Pousser la branche EPIC
git push -u origin EPIC
```

### 3. Vérification

Une fois poussé, tu devrais voir sur GitHub :
- Branche `main` avec le commit "EPIC 0 et 1: Project setup, database models, and initial API"
- Branche `EPIC` (identique à main pour l'instant)

### Alternative : Utiliser SSH au lieu de HTTPS

Si tu préfères SSH (plus pratique, pas de mot de passe à chaque push) :

```bash
# Ajouter le remote avec SSH
git remote add origin git@github.com:amn-sdk/CleanInvoice-AI.git

# Puis push normalement
git branch -M main
git push -u origin main
git push -u origin EPIC
```

**Note** : Pour SSH, il faut d'abord configurer une clé SSH sur GitHub :
https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## Commandes déjà exécutées ✅

- ✅ `git init`
- ✅ `git config user.name "amn-sdk"`
- ✅ `git config user.email "amine.saddik@edu.esiee.fr"`
- ✅ `git add .`
- ✅ `git commit -m "EPIC 0 et 1: Project setup, database models, and initial API"`
- ✅ `git checkout -b EPIC`

**Tu es actuellement sur la branche EPIC** 🎯

Il ne reste plus qu'à créer le repo sur GitHub et faire le push !
