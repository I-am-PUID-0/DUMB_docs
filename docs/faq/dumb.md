---
title: DUMB FAQ
---

# DUMB FAQ

Below are some common questions and solutions related to **DUMB**.

---
## ❓ Frequently Asked Questions (FAQ)

### Does the **DUMB** image have the latest version of `x`

The GitHub repo for **DUMB** use many continuous integration and continuous deployment (CI/CD) workflows to ensure proper building, reporting, and updating of the images.

For example, the [Check for New Release Tags](https://github.com/I-am-PUID-0/DUMB/actions/workflows/fetch-latest-tags.yml) workflow is automated to run every three hours and check for updates to the various services/projects utilized in DUMB. If an update is found, the [Docker Image CI](https://github.com/I-am-PUID-0/DUMB/actions/workflows/docker-image.yml) workflow is called to build a new image with the latest services. 

### What versions are in the latest **DUMB** image

Similar to the above question, and the answer is usually the latest; however, if there has been a recent release and the [Check for New Release Tags](https://github.com/I-am-PUID-0/DUMB/actions/workflows/fetch-latest-tags.yml) workflow has not run yet, then there my be disparity. 

To check, click on one of the [Docker Image CI](https://github.com/I-am-PUID-0/DUMB/actions/workflows/docker-image.yml) jobs to see the `Build Summary`

Example `Build Summary` below:
![Build Summary](../assets/images/build_summary.PNG)