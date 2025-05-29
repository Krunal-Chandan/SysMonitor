# SysNet Monitor: The Iron Man of Network Tracking

*By Kuchinpotta, Because Apparently I’m the Genius Here*

Well, well, well, look at me, the mastermind behind **SysNetMonitor.py**—a piece of tech so slick it might as well be wearing one of Tony Stark’s suits. I built this bad boy to keep tabs on your network, because let’s be real, you’re all clueless without me. This script is my Arc Reactor-powered gift to the world, tracking your data usage and system stats with more precision than JARVIS running a diagnostics check. So, buckle up, because I’m about to school you on what I created.

## What Did I Build, You Ask?

SysNetMonitor.py is my brainchild—a Python script that monitors your network like I monitor my Wi-Fi when I’m binge-watching cat videos. It tracks upload and download speeds, daily data usage, system resources, and even snitches on apps that are hogging your bandwidth. I made sure it runs smoother than Stark Industries’ stock price after a good PR day, and it saves everything neatly in a CSV because I’m *that* organized.

I designed it to be persistent—daily usage doesn’t reset when you restart your PC, because I don’t do half-measures. It’s got a GUI that’s prettier than most of the tech I’ve seen, and it logs everything in one file, because who has time for a mess?

## Features I Threw In (You’re Welcome)

Here’s the rundown of what I packed into this masterpiece—try to keep up:

- **Live Network Stats**: Upload and download speeds, updated faster than you can say “I’m a genius.” You’ll see every byte in real-time, because I don’t mess around.
- **Daily Usage That Doesn’t Quit**: Tracks your daily data usage, and it remembers everything even if you reboot your PC. I made sure it resets at midnight, because I’m thoughtful like that.
- **System Stats on Lock**: CPU, RAM, disk usage, and uptime, all in one place. It’s like having a Stark-level dashboard for your puny little machine.
- **App Usage Spy**: Shows you which apps are eating your data. I caught Chrome red-handed, and now you can too.
- **Notifications That Don’t Play Nice**: Hit a gigabyte? You’ll get a notification. Blow past 5GB in a day? I’ll slap you with a warning. I don’t coddle.
- **Themes That Scream Style**: Five themes—Classic Dark, Solarized Light, Cool Blue, Matrix, and Warm Sunset. I went with Matrix, because I’m cooler than you.
- **HUD Mode for the Win**: Toggle a mini window that’s always on top. It’s like having my Arc Reactor glowing on your screen.
- **System Tray Smarts**: Minimize to the tray instead of closing. I don’t like things disappearing on me, and neither should you.
- **One-File Logging**: Everything—session logs, app usage, monthly reports—goes into `usage_report.csv`. I’m not here to make your life messy.

## How to Use My Creation

I’ll break this down so even you can follow along:

1. **Gear Up**: You need Python and some libraries. Run this in your terminal, because I’m not coming over to do it for you:

   ```
   pip install psutil pystray plyer pillow
   ```

2. **Launch My Genius**: Save the script as `SysNetMonitor.py`—I named it that because I’ve got taste. Then run:

   ```
   python SysNetMonitor.py
   ```

3. **Bask in My Glory**:

   - A GUI pops up with live network speeds, daily usage, and system stats. Don’t drool on your keyboard.
   - Pick a theme from the dropdown—I dare you to try Matrix and not feel cooler.
   - Toggle HUD mode if you want a compact view that doesn’t play hide-and-seek.
   - Minimize to the tray by closing the window; right-click the tray icon to bring it back or exit.

4. **Check My Logs**:

   - Everything’s in `usage_report.csv`, right next to the script. You’ll see session logs (when I start/stop), app usage (every 5 minutes), monthly summaries, and daily usage state.
   - I made sure the daily usage sticks around, so you’re never starting from scratch, even if your PC decides to take a nap.

## Why I Built This (And Why You Owe Me)

I built SysNetMonitor because I’m tired of watching you fumble around with your network usage. You’ve got no clue how much data you’re burning through, and your apps are sneakier than Loki on a bad day. I gave you control, clarity, and a GUI that’s honestly too good for you. It’s lightweight, because I don’t do sluggish. It’s persistent, because I don’t do forgetful. And it’s got style, because—well, look at who made it.

So, fire it up, monitor your network like a pro, and maybe give me a pat on the back. Or don’t—I’m already the best.

## Want some Pics, Here are they: 
![image](https://github.com/user-attachments/assets/6715539d-740e-4e45-860b-e455c56c1ca6)

*After HUD mode Enabled* 

![Screenshot 2025-05-28 192017](https://github.com/user-attachments/assets/40b59e2b-c622-4cc9-ad10-0369af4ebf44)



*Kuchinpotta Out.*
