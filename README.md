# 🎮 EpicGames-Freebie-Notifier  

A **fully automated Python program** that fetches daily **Epic Games freebie** offers and posts them to a **Discord server** with **rich embedded messages**.  

## 🚀 Features  
✅ Fetches **free games** from Epic Games daily  
✅ Sends **game name, link, image, original price, and remaining free days**  
✅ **Prevents duplicate notifications** (Tracks games in `posted.json`)  
✅ **Auto-updates** game details to avoid incorrect information  
✅ **Fully automated** using GitHub Actions (Runs daily at **12:00 AM UTC**)  

---

## 🛠️ Installation  

### 1️⃣ Clone the Repository  
```sh
git clone https://github.com/nayandas69/EpicGames-Freebie-Notifier.git
cd EpicGames-Freebie-Notifier
```

### 2️⃣ Install Dependencies  
```sh
pip install -r requirements.txt
```

### 3️⃣ Set Up GitHub Secrets  
You need to add your **Discord Webhook URL** as a secret in GitHub:  
1. Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**  
2. Click **New repository secret**  
3. Add the following secret:  
   - **Name**: `DISCORD_WEBHOOK`  
   - **Value**: _(Your Discord Webhook URL)_  

### 4️⃣ Run Manually (Optional)  
You can manually run the script on your local machine:  
```sh
python main.py
```


## 🔄 How It Works  

### 🕵️ Step 1: Fetch Free Games  
The script fetches **daily free games** from Epic Games' official API.

### 📌 Step 2: Check for New Freebies  
It **compares new games** with previously posted ones (stored in `posted.json`).  

### 💬 Step 3: Send Rich Discord Message  
If a **new free game** is found, it sends a **rich embedded message** with:  
- **Game Name**  
- **Game Link**  
- **Game Image**  
- **Original Price (Before Free)**  
- **Days Left to Claim**  

### 🔄 Step 4: Update `posted.json`  
The program **updates the `posted.json` file** to prevent duplicate notifications.  

### 🔁 Step 5: Repeat Daily (Automated)  
The program runs **daily at 12:00 AM UTC** via **GitHub Actions**.  


## ⚙️ Automation (GitHub Actions)  
This project **automatically runs** every day at **12:00 AM UTC** and posts free game details to Discord.  

### Workflow Trigger Conditions  
✅ **Every day at 12:00 AM UTC**  
✅ **On every push to `main` branch**  
✅ **Manually triggered (Optional)**  

### How to Enable Automation  
Just **push this project** to GitHub and set up the required **secrets**. GitHub Actions will handle everything.  


## ❓ FAQ  

### 💬 How do I get a Discord Webhook?  
1. Open Discord  
2. Go to **Server Settings** → **Integrations**  
3. Click **Create Webhook** → Copy the **Webhook URL**  
4. Add it as **GitHub Secret** (`DISCORD_WEBHOOK`)  

### 💬 Can I run this script manually?  
Yes! Run:  
```sh
python main.py
```

### 💬 Will the script send duplicate game notifications?  
No! The script **stores previously notified games** in `posted.json` and avoids re-posting them.  


## 📜 License  
This project is **open-source** and available under the **MIT License**.  

✅ **Enjoy free games effortlessly! 🎮**

