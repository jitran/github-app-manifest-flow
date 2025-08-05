# GitHub App Manifest Flow

This is an example implementation of the [GitHub App Manifest flow](https://docs.github.com/en/enterprise-cloud@latest/apps/sharing-github-apps/registering-a-github-app-from-a-manifest#implementing-the-github-app-manifest-flow), built with Copilot.

It consists of a webserver that serves GitHub App manifests and handles redirections after the app registration. The server needs to be publicly resolvable for GitHub to forward the redirection requests.

## Example end to end implementation

```mermaid
sequenceDiagram
    participant Requestor
    participant GitHub
    participant Server
    participant Secure Storage
    participant Support Engineer

    Requestor->>GitHub: Submit issue with app details
    GitHub->>Server: Add new app manifest into queue via actions
    Support Engineer->>Server: Access server to register GitHub App
    Server->>GitHub: Register GitHub App with manifest
    GitHub->>Server: Return temporary code
    Server->>GitHub: Retrieve app credentials using code
    Server->>Secure Storage: Store app credentails
    Server->>GitHub: Mark issue as closed
```


## Setup Ngrok
You can use ngrok to resolve public requests from GitHub to your internal server.

Follow [ngrok instructions](https://dashboard.ngrok.com/) to install and configure ngrok.

In a separate terminal, run:
```shell
ngrok http http://127.0.0.1:5000
```

Take note of the domain `<uuid>.ngrok-free.app` from the output, i.e.
```
https://aabbccddeeff.ngrok-free.app -> http://127.0.0.1:5000
```


## Start Server

```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

export SERVER_URL=https://<PUBLIC DOMAIN>
python3 server.py
```


### Example requests screen

![Example requests screen](example.png)