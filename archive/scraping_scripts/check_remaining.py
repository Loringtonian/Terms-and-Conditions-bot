#!/usr/bin/env python3
"""
Quick check of what apps remain to be scraped
"""
from src.terms_analyzer.utils.storage import StorageManager

ALL_APPS = [
    "Google Play Services", "YouTube", "Google Maps", "Google Chrome", "Gmail", 
    "Google Photos", "Google Drive", "Google (Search)", "Google Calendar", "Google Meet", 
    "Google Messages", "Google Pay", "Google Assistant", "Google Translate", "Google Keep", 
    "Google Docs", "Google Sheets", "Google Slides", "YouTube Music", "Gboard", 
    "Android System WebView", "Android Accessibility Suite", "Speech Services by Google", 
    "Facebook", "Messenger", "WhatsApp Messenger", "WhatsApp Business", "Instagram", 
    "Threads", "TikTok", "Snapchat", "X", "Telegram", "LinkedIn", "Zoom", 
    "Microsoft Teams", "Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint", 
    "Microsoft OneDrive", "Microsoft Outlook", "Dropbox", "PayPal", "Amazon Shopping", 
    "eBay", "SHEIN", "DoorDash", "Uber", "Lyft", "Spotify", "Netflix", 
    "Disney+", "Peacock TV", "Max", "Hulu", "Prime Video", "CapCut", "Canva", 
    "Picsart", "SHAREit", "MX Player", "Truecaller", "Google One", "Google Lens", 
    "Tinder", "Bumble", "Hinge", "Duolingo", "Audible", "Kindle", "Shazam", 
    "Google TV", "Crunchyroll", "Roblox", "Fortnite", "PUBG MOBILE", "Free Fire", 
    "Candy Crush Saga", "Subway Surfers", "Temple Run 2", "Clash of Clans", 
    "Clash Royale", "8 Ball Pool", "Hill Climb Racing", "Pokémon GO", "Royal Match", 
    "Last War: Survival", "Block Blast", "IceBlock", "Kingshot", "Coin Master", 
    "Whiteout Survival", "Paramount+", "Airbnb", "Waze", "Google Maps Go", 
    "Files by Google", "Genshin Impact", "Uber Eats", "WeChat"
]

def main():
    storage = StorageManager()
    processed = []
    remaining = []
    
    for app in ALL_APPS:
        if storage.load_terms(app):
            processed.append(app)
        else:
            remaining.append(app)
    
    print(f"📊 SCRAPING STATUS:")
    print(f"📱 Total apps: {len(ALL_APPS)}")
    print(f"✅ Processed: {len(processed)}")
    print(f"⏳ Remaining: {len(remaining)}")
    print(f"📈 Progress: {(len(processed)/len(ALL_APPS)*100):.1f}%")
    
    if remaining:
        print(f"\n⏳ REMAINING APPS ({len(remaining)}):")
        for i, app in enumerate(remaining, 1):
            print(f"   {i:2d}. {app}")
    else:
        print("\n🎉 ALL APPS COMPLETED!")

if __name__ == "__main__":
    main()