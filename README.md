# beckhoff-linux-package-browser
Beckhoff offers PLC's with Linux Kernel (eg. CX9240 or CX82xx) and uses a package server to install several TwinCAT functions.
But without a real PLC it's cumbursome to see available packages along with de different versions.

This tool is generated with Clause Sonnet 4.6. It's a python script which you can run locally. It runs a local webserver and automatically opens a webpage.
Here you can enter your Beckhoff credentials and select the stable/testing feed and select your platform amd64/arm64 (or you can upload the package list downloaded from deb.beckhoff.com).
After this selection the tool logs in on deb.beckhoff.com downloads and parses the available packages and gives an overview of all available packages.

<img width="495" height="575" alt="image" src="https://github.com/user-attachments/assets/c3ce5120-34ab-46f3-8aed-9e462759d7aa" />

<img width="1882" height="720" alt="image" src="https://github.com/user-attachments/assets/c307dc11-5a79-4378-a0ad-7b53537454cb" />
