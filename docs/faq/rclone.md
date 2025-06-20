# rclone FAQ

Below are some common questions and solutions related to using **rclone** with **DMB**.

---

## ❓ Frequently Asked Questions (FAQ)

### I think I might be rate limited by the debrid service - seeing `423` errors.

Add `- RCLONE_TSP_LIMIT=10` to the environment variable section of the compose.

---

### How do I enable rclone filtering to include only specific resolutions? 


#### Using rclone [--exclude](https://rclone.org/filtering/#exclude-exclude-files-matching-pattern) pattern matching:


##### Example docker-compose to include only 4k|2160|UHD content. 

Add `- RCLONE_EXCLUDE=**/**{{(?i)(1080|720|480)}}**` to the environment variable section of the compose.


##### Example docker-compose to exclude only 4k|2160|UHD content. 

Add `- RCLONE_EXCLUDE=**/**{{(?i)(4k|uhd|2160)}}**` to the environment variable section of the compose. 


#### Using rclone [--filter-from](https://rclone.org/filtering/#filter-from-read-filtering-patterns-from-a-file) pattern matching:


##### Example docker-compose to include only 4k|2160|UHD content. 

Add `- RCLONE_FILTER_FROM=/config/filter_include_2160.txt` to the environment variable section of the compose and add the below content to a `filter_include_2160.txt` file in the config directory for the container. 


###### Example filter_include_2160.txt

```bash
- **/**{{(?i)(1080|720|480)}}**
+ *
```


##### Example docker-compose to exclude only 4k|2160|UHD content. 
Add `- RCLONE_FILTER_FROM=/config/filter_exclude_2160.txt` to the environment variable section of the compose and the below content to a `filter_exclude_2160.txt` file in the config directory for the container.


###### Example filter_exclude_2160.txt

```bash
- **/**{{(?i)(4k|uhd|2160)}}**
+ *
```

---

### Error response from daemon: path `/your/host/path/mnt` is mounted on `/` but it is not a shared mount.

From the host OS, enter `sudo mount --make-rshared /` 

Or if using a NAS device `sudo mount --make-rshared /volume1/` 

If neither of the above resolves the error, ensure that docker is not installed via snap. Install docker via apt. 

!!! note 
    `sudo mount --make-rshared` does not persist reboots, so it will need to be run each time WSL2 or Windows is restarted. Alternatively, see the below guide for automatically executing the command on startup for Ubuntu.


### Ubuntu systemd service:

To make Ubuntu run a command like `sudo mount --make-rshared /` on startup, you can use a systemd service unit that executes this command at boot.

Systemd is a system and service manager for Linux operating systems, which allows you to specify custom startup tasks through service units.

Here's how you can do it:


#### Create a systemd service file:
First, you need to create a new systemd service file. You can do this by creating a file in the /etc/systemd/system directory. Let's call this file make-rshared.service.

Open a terminal and use your favorite text editor to create this file. You'll need sudo privileges to create a file in this directory. For example, using nano:

```bash
sudo nano /etc/systemd/system/make-rshared.service
```

Add the following contents to the service file:

```bash
[Unit]
Description=Make root filesystem rshared
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/bin/mount --make-rshared /
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```


#### Enable and start the service:
After saving the file, you need to reload the systemd daemon to recognize your new service and then enable the service to start on boot:

```bash
sudo systemctl daemon-reload
sudo systemctl enable make-rshared.service
```
To start the service immediately without rebooting, you can use:

```bash
sudo systemctl start make-rshared.service
```


#### Verify the service is active:

After rebooting or starting the service, you can check its status to ensure it's active and has run successfully:

```bash
sudo systemctl status make-rshared.service
```


## 📎 Related Pages
- [Rclone Configuration](../services/rclone.md)