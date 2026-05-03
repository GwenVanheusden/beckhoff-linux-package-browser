# beckhoff-linux-package-analyzer
Beckhoff offers PLC's with Linux Kernel (eg. CX9240 or CX82xx) and uses a package server to install several TwinCAT functions.
But without a real PLC it's cumbursome to see available packages along with de different versions. Beckhoff also uses a stable feed and testing/outdated feed.

This tool is generated with Clause Sonnet 4.6. It's a python script which you can run locally. It set's up a local webserver and automatically opens a webpage.
Here you can enter your Beckhoff credentials and select the stable/testing feed and select your platform amd64/arm64 or you can upload the package list downloaded from deb.beckhoff.com.
After this selection the tool logs in on deb.beckhoff.com downloads and parses the available packages and gives a nice list of available packages.

<img width="495" height="610" alt="image" src="https://github.com/user-attachments/assets/be72bb8d-ccb3-45cd-ad0e-dadcc639b766" />


<img width="1872" height="678" alt="image" src="https://github.com/user-attachments/assets/321b2810-28f4-41da-b4b3-affe10a935d1" />

