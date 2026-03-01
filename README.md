# Python NetCat Tool (BHP Net Tool)

## 📖 About This Project
This is a custom implementation of a NetCat-like tool written in Python 3. This project was developed as part of my deep-dive into network security and systems programming, based on the concepts and foundations provided in the book **"Black Hat Python"** by Justin Seitz and Tim Arnold.

As a **Software Engineering** student, I built this to better understand socket programming, multi-threading, and how low-level network communication works between a client and a server.

## 🚀 Features
* **Reverse Shell:** Open a command shell on a remote target.
* **File Upload:** Send files from a client to a listening server.
* **Command Execution:** Execute specific system commands remotely and receive the output.
* **Interactive Mode:** Connect to any open port to send and receive data manually.

## 🛠️ Usage
### 1. Start a Listener (The Server)
To open a command shell on a specific port:
```bash
python3 netcat.py -t 0.0.0.0 -p 5555 -l -c

### How to push this new file to GitHub:
1.  `git add README.md`
2.  `git commit -m "Add professional README with attribution to Black Hat Python"`
3.  `git push origin main`
