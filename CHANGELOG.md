# Changelog

## [1.8.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.7.0...1.8.0) (2026-01-26)


### ✨ Features

* **banner:** Add custom banner to indicating ongoing migration ([92bad2b](https://github.com/I-am-PUID-0/DUMB_docs/commit/92bad2b1f346b22329abb7e192f847066c7cd0c9))
* **docs:** add comprehensive reference documentation for configuration schema, core service routing, environment variables, multi-instance setup, service ports, and individual services (Huntarr, Seerr, Tautulli) ([88abe64](https://github.com/I-am-PUID-0/DUMB_docs/commit/88abe642b7dd712c60e3a44382446f6ba15cdec1))
* **docs:** add Plex Media Server migration instructions and hardware transcoding setup ([d58ad52](https://github.com/I-am-PUID-0/DUMB_docs/commit/d58ad52eb491cf8d1b351283d43215813795a775))
* **docs:** enhance documentation for Plex Media Server integration and configuration ([af5c5c1](https://github.com/I-am-PUID-0/DUMB_docs/commit/af5c5c17b2357b737ac0a982f2b31c985c2a8120))
* update documentation for core services and integrations ([efa285c](https://github.com/I-am-PUID-0/DUMB_docs/commit/efa285ce177981aaf26fd65966879fbb1649ea77))
* uplift docs from mkdocs to zensical ([#22](https://github.com/I-am-PUID-0/DUMB_docs/issues/22)) ([5548ee3](https://github.com/I-am-PUID-0/DUMB_docs/commit/5548ee36a61eb14e83f78db19fcb9e64949d5a6f))


### 🐛 Bug Fixes

* **changelog:** deployment trigger for Changelog updates ([814bbe1](https://github.com/I-am-PUID-0/DUMB_docs/commit/814bbe1de49d863ce9d5ea724c21afb979e7cbac))
* **deps:** bump actions/checkout from 3 to 6 ([#25](https://github.com/I-am-PUID-0/DUMB_docs/issues/25)) ([bfbddc3](https://github.com/I-am-PUID-0/DUMB_docs/commit/bfbddc3002b9eab0e9c20f345dc81a03951da9bb))
* **deps:** bump actions/setup-python from 5 to 6 ([#28](https://github.com/I-am-PUID-0/DUMB_docs/issues/28)) ([026b030](https://github.com/I-am-PUID-0/DUMB_docs/commit/026b030e706fa28f942f077ccd27112f9ba0473e))
* **deps:** bump hmarr/auto-approve-action from 3 to 4 ([#27](https://github.com/I-am-PUID-0/DUMB_docs/issues/27)) ([1ba1775](https://github.com/I-am-PUID-0/DUMB_docs/commit/1ba17751401af3df8135e5ffce380269db0f4c77))
* **deps:** bump peaceiris/actions-gh-pages from 3 to 4 ([#24](https://github.com/I-am-PUID-0/DUMB_docs/issues/24)) ([2e3fff3](https://github.com/I-am-PUID-0/DUMB_docs/commit/2e3fff365c3da1de5c29b5ce98b1a1220d67af05))
* **deps:** bump peter-evans/create-pull-request from 5 to 8 ([#26](https://github.com/I-am-PUID-0/DUMB_docs/issues/26)) ([ce19d3f](https://github.com/I-am-PUID-0/DUMB_docs/commit/ce19d3f3d92e813f23940e8b55bf080711686f64))
* **docs:** correct punctuation in tip regarding mount structure and propagation ([14255b3](https://github.com/I-am-PUID-0/DUMB_docs/commit/14255b3b24c8855f2ece396b4f10f4f5de3bc767))
* **docs:** correct YAML front matter formatting in Services Overview ([64b1885](https://github.com/I-am-PUID-0/DUMB_docs/commit/64b1885058a260cb9e33a98c6af1e1899c425e5a))
* **docs:** update rclone configuration and enhance key descriptions ([5ebc920](https://github.com/I-am-PUID-0/DUMB_docs/commit/5ebc920913bb62b6392843187e2f5bdfdc6e64cc))
* **docs:** update riven_frontend configuration and add origin key description ([8306b07](https://github.com/I-am-PUID-0/DUMB_docs/commit/8306b071bc07e3182dbf4c477ed341c43fd09169))
* **docs:** update troubleshooting tips for hardware transcoding and onboarding process ([e4c8922](https://github.com/I-am-PUID-0/DUMB_docs/commit/e4c89224b093c14154c739021983657dabc6066c))
* **rclone:** corrects link to decypharr page ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* update decypharr ([3c115a3](https://github.com/I-am-PUID-0/DUMB_docs/commit/3c115a3e3c1b70509605042075fc7e0d76374ff1))
* **workflow:** change PR merge strategy to squash for automated changelog updates ([a123926](https://github.com/I-am-PUID-0/DUMB_docs/commit/a12392634aa35be4cc0c0aa31b76a73c08df8b4f))
* **workflow:** improve changelog update logic and user configuration ([01c44fe](https://github.com/I-am-PUID-0/DUMB_docs/commit/01c44feab56c3c2d11540af19244f38100d3826e))
* **workflow:** reorder steps for auto-approval and merging of changelog PRs ([bf2b5a8](https://github.com/I-am-PUID-0/DUMB_docs/commit/bf2b5a81522f310ea963b9fd2a6c50944234c31e))
* **workflow:** replace commit and push logic with pull request creation for changelog updates ([01fcb3c](https://github.com/I-am-PUID-0/DUMB_docs/commit/01fcb3c3d55d786f5e3a5c6396cb2e94a3fc9bdb))
* **workflow:** update condition for extracting pull request number ([86f5d0d](https://github.com/I-am-PUID-0/DUMB_docs/commit/86f5d0df149d72eca62bfd546f6125cbce0af94b))
* **workflow:** update condition for extracting pull request number to ensure valid URL check ([1e33c2f](https://github.com/I-am-PUID-0/DUMB_docs/commit/1e33c2fd54faf9571c8e16cfb8ef719d6f09cb7f))
* **workflow:** update deploy condition to include 'Automated Changelog Update' title ([f70d45f](https://github.com/I-am-PUID-0/DUMB_docs/commit/f70d45ff19cdb262a0d5a26ea4a8342ae226daa2))
* **workflow:** update token for creating pull requests to use GITHUB_TOKEN ([f9a7130](https://github.com/I-am-PUID-0/DUMB_docs/commit/f9a7130290da03ed8db52a699b7ae6051a2f7111))


### 🤡 Other Changes

* **docs:** update documentation and configs ([812ccbe](https://github.com/I-am-PUID-0/DUMB_docs/commit/812ccbe56cee22b01a082b787902043b42ed58dd))
* **master:** release 1.0.1 ([#1](https://github.com/I-am-PUID-0/DUMB_docs/issues/1)) ([88c7c8d](https://github.com/I-am-PUID-0/DUMB_docs/commit/88c7c8d327c3d5ea8aeaa1b05a12fcfa7e2349c1))
* **master:** release 1.1.0 ([#2](https://github.com/I-am-PUID-0/DUMB_docs/issues/2)) ([79599d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/79599d8566b26301637053d6298d161b21daf07d))
* **master:** release 1.2.0 ([#3](https://github.com/I-am-PUID-0/DUMB_docs/issues/3)) ([e5b7bcf](https://github.com/I-am-PUID-0/DUMB_docs/commit/e5b7bcf2f89da59303f762617619d2c5edd4adda))
* **master:** release 1.2.1 ([#4](https://github.com/I-am-PUID-0/DUMB_docs/issues/4)) ([2020204](https://github.com/I-am-PUID-0/DUMB_docs/commit/2020204b527034edd12caf716d473f080a1302cb))
* **master:** release 1.2.2 ([#5](https://github.com/I-am-PUID-0/DUMB_docs/issues/5)) ([977579f](https://github.com/I-am-PUID-0/DUMB_docs/commit/977579ffcafb4d5cc502200c3ef0135ccae2ccb6))
* **master:** release 1.2.3 ([#6](https://github.com/I-am-PUID-0/DUMB_docs/issues/6)) ([c7a6416](https://github.com/I-am-PUID-0/DUMB_docs/commit/c7a64169ab2e92918b6d399f886ab3bc7bc769b1))
* **master:** release 1.2.4 ([#10](https://github.com/I-am-PUID-0/DUMB_docs/issues/10)) ([e55ca5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/e55ca5f48e7a3c5bfe73e26f37950cffc0499993))
* **master:** release 1.3.0 ([#13](https://github.com/I-am-PUID-0/DUMB_docs/issues/13)) ([f599724](https://github.com/I-am-PUID-0/DUMB_docs/commit/f5997249905cb61ebad6f04f633278a7c13b01b7)), closes [#11](https://github.com/I-am-PUID-0/DUMB_docs/issues/11)
* **master:** release 1.3.1 ([#14](https://github.com/I-am-PUID-0/DUMB_docs/issues/14)) ([12131d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/12131d8ba9fb253b8596c42ba3ec30dbe419be44))
* **master:** release 1.3.2 ([#15](https://github.com/I-am-PUID-0/DUMB_docs/issues/15)) ([0c918fd](https://github.com/I-am-PUID-0/DUMB_docs/commit/0c918fd4bec7efe446c201a2bc877cce5e776ee1))
* **master:** release 1.3.3 ([#16](https://github.com/I-am-PUID-0/DUMB_docs/issues/16)) ([d6555d9](https://github.com/I-am-PUID-0/DUMB_docs/commit/d6555d9042efc17cfbc0919325afbb77a9a4b1c4))
* **master:** release 1.3.4 ([#18](https://github.com/I-am-PUID-0/DUMB_docs/issues/18)) ([24ee66f](https://github.com/I-am-PUID-0/DUMB_docs/commit/24ee66fa22c010e8fa242e52ffd41ee71df08989))
* **master:** release 1.3.5 ([#19](https://github.com/I-am-PUID-0/DUMB_docs/issues/19)) ([3312143](https://github.com/I-am-PUID-0/DUMB_docs/commit/33121432966f148e29d765daf54a1d5726bf3c4e))
* **master:** release 1.4.0 ([#21](https://github.com/I-am-PUID-0/DUMB_docs/issues/21)) ([7a5e870](https://github.com/I-am-PUID-0/DUMB_docs/commit/7a5e8703cd178109d659ddd9623d5963020b03af))
* **master:** release 1.5.0 ([#23](https://github.com/I-am-PUID-0/DUMB_docs/issues/23)) ([cb9b73f](https://github.com/I-am-PUID-0/DUMB_docs/commit/cb9b73f3e276ba7bf0293ea57d6641b2cbafc542))
* **master:** release 1.6.0 ([#30](https://github.com/I-am-PUID-0/DUMB_docs/issues/30)) ([74a64b9](https://github.com/I-am-PUID-0/DUMB_docs/commit/74a64b9d7905ada8806677ce0c5576b386504761))
* **master:** release 1.7.0 ([#32](https://github.com/I-am-PUID-0/DUMB_docs/issues/32)) ([4c12e2f](https://github.com/I-am-PUID-0/DUMB_docs/commit/4c12e2f757047510a06fef66e3471fedaba3e745))


### 📖 Documentation

* Add Decypharr service documentation ([19c8c50](https://github.com/I-am-PUID-0/DUMB_docs/commit/19c8c5078845956d066117b18dd09a6f1042dc21))
* Add guidance for host-based media server mount path consistency ([3babdaf](https://github.com/I-am-PUID-0/DUMB_docs/commit/3babdaf8821af088c6079062fd4a037c25f07a4a))
* **deployment:** update Docker and WSL guides with additional notes for sharing mounts ([f1f6ecf](https://github.com/I-am-PUID-0/DUMB_docs/commit/f1f6ecff1b77c43445d00a7a50b4e330e8616104))
* **docker:** Improves the Docker deployment guide by refining notes and tips for clarity. ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* init push of DUMB docs ([9d59855](https://github.com/I-am-PUID-0/DUMB_docs/commit/9d59855de0c7ff87fb7389863050876888da5a82))
* Update CLI Debrid documentation ([288e49b](https://github.com/I-am-PUID-0/DUMB_docs/commit/288e49b43a2eb394e4fd3f2ed88616a550a587d3)), closes [#12](https://github.com/I-am-PUID-0/DUMB_docs/issues/12)
* update docker.md ([9bd9e5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/9bd9e5ff203709f97d6487cd39520206faa0a7ca))

## [1.7.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.6.0...1.7.0) (2026-01-26)


### ✨ Features

* **banner:** Add custom banner to indicating ongoing migration ([92bad2b](https://github.com/I-am-PUID-0/DUMB_docs/commit/92bad2b1f346b22329abb7e192f847066c7cd0c9))
* **docs:** add comprehensive reference documentation for configuration schema, core service routing, environment variables, multi-instance setup, service ports, and individual services (Huntarr, Seerr, Tautulli) ([88abe64](https://github.com/I-am-PUID-0/DUMB_docs/commit/88abe642b7dd712c60e3a44382446f6ba15cdec1))
* **docs:** add Plex Media Server migration instructions and hardware transcoding setup ([d58ad52](https://github.com/I-am-PUID-0/DUMB_docs/commit/d58ad52eb491cf8d1b351283d43215813795a775))
* **docs:** enhance documentation for Plex Media Server integration and configuration ([af5c5c1](https://github.com/I-am-PUID-0/DUMB_docs/commit/af5c5c17b2357b737ac0a982f2b31c985c2a8120))
* update documentation for core services and integrations ([efa285c](https://github.com/I-am-PUID-0/DUMB_docs/commit/efa285ce177981aaf26fd65966879fbb1649ea77))
* uplift docs from mkdocs to zensical ([#22](https://github.com/I-am-PUID-0/DUMB_docs/issues/22)) ([5548ee3](https://github.com/I-am-PUID-0/DUMB_docs/commit/5548ee36a61eb14e83f78db19fcb9e64949d5a6f))


### 🐛 Bug Fixes

* **changelog:** deployment trigger for Changelog updates ([814bbe1](https://github.com/I-am-PUID-0/DUMB_docs/commit/814bbe1de49d863ce9d5ea724c21afb979e7cbac))
* **deps:** bump actions/checkout from 3 to 6 ([#25](https://github.com/I-am-PUID-0/DUMB_docs/issues/25)) ([bfbddc3](https://github.com/I-am-PUID-0/DUMB_docs/commit/bfbddc3002b9eab0e9c20f345dc81a03951da9bb))
* **deps:** bump actions/setup-python from 5 to 6 ([#28](https://github.com/I-am-PUID-0/DUMB_docs/issues/28)) ([026b030](https://github.com/I-am-PUID-0/DUMB_docs/commit/026b030e706fa28f942f077ccd27112f9ba0473e))
* **deps:** bump hmarr/auto-approve-action from 3 to 4 ([#27](https://github.com/I-am-PUID-0/DUMB_docs/issues/27)) ([1ba1775](https://github.com/I-am-PUID-0/DUMB_docs/commit/1ba17751401af3df8135e5ffce380269db0f4c77))
* **deps:** bump peaceiris/actions-gh-pages from 3 to 4 ([#24](https://github.com/I-am-PUID-0/DUMB_docs/issues/24)) ([2e3fff3](https://github.com/I-am-PUID-0/DUMB_docs/commit/2e3fff365c3da1de5c29b5ce98b1a1220d67af05))
* **deps:** bump peter-evans/create-pull-request from 5 to 8 ([#26](https://github.com/I-am-PUID-0/DUMB_docs/issues/26)) ([ce19d3f](https://github.com/I-am-PUID-0/DUMB_docs/commit/ce19d3f3d92e813f23940e8b55bf080711686f64))
* **docs:** correct punctuation in tip regarding mount structure and propagation ([14255b3](https://github.com/I-am-PUID-0/DUMB_docs/commit/14255b3b24c8855f2ece396b4f10f4f5de3bc767))
* **docs:** correct YAML front matter formatting in Services Overview ([64b1885](https://github.com/I-am-PUID-0/DUMB_docs/commit/64b1885058a260cb9e33a98c6af1e1899c425e5a))
* **docs:** update rclone configuration and enhance key descriptions ([5ebc920](https://github.com/I-am-PUID-0/DUMB_docs/commit/5ebc920913bb62b6392843187e2f5bdfdc6e64cc))
* **docs:** update riven_frontend configuration and add origin key description ([8306b07](https://github.com/I-am-PUID-0/DUMB_docs/commit/8306b071bc07e3182dbf4c477ed341c43fd09169))
* **docs:** update troubleshooting tips for hardware transcoding and onboarding process ([e4c8922](https://github.com/I-am-PUID-0/DUMB_docs/commit/e4c89224b093c14154c739021983657dabc6066c))
* **rclone:** corrects link to decypharr page ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* update decypharr ([3c115a3](https://github.com/I-am-PUID-0/DUMB_docs/commit/3c115a3e3c1b70509605042075fc7e0d76374ff1))
* **workflow:** change PR merge strategy to squash for automated changelog updates ([a123926](https://github.com/I-am-PUID-0/DUMB_docs/commit/a12392634aa35be4cc0c0aa31b76a73c08df8b4f))
* **workflow:** improve changelog update logic and user configuration ([01c44fe](https://github.com/I-am-PUID-0/DUMB_docs/commit/01c44feab56c3c2d11540af19244f38100d3826e))
* **workflow:** reorder steps for auto-approval and merging of changelog PRs ([bf2b5a8](https://github.com/I-am-PUID-0/DUMB_docs/commit/bf2b5a81522f310ea963b9fd2a6c50944234c31e))
* **workflow:** replace commit and push logic with pull request creation for changelog updates ([01fcb3c](https://github.com/I-am-PUID-0/DUMB_docs/commit/01fcb3c3d55d786f5e3a5c6396cb2e94a3fc9bdb))
* **workflow:** update condition for extracting pull request number ([86f5d0d](https://github.com/I-am-PUID-0/DUMB_docs/commit/86f5d0df149d72eca62bfd546f6125cbce0af94b))
* **workflow:** update condition for extracting pull request number to ensure valid URL check ([1e33c2f](https://github.com/I-am-PUID-0/DUMB_docs/commit/1e33c2fd54faf9571c8e16cfb8ef719d6f09cb7f))
* **workflow:** update deploy condition to include 'Automated Changelog Update' title ([f70d45f](https://github.com/I-am-PUID-0/DUMB_docs/commit/f70d45ff19cdb262a0d5a26ea4a8342ae226daa2))
* **workflow:** update token for creating pull requests to use GITHUB_TOKEN ([f9a7130](https://github.com/I-am-PUID-0/DUMB_docs/commit/f9a7130290da03ed8db52a699b7ae6051a2f7111))


### 🤡 Other Changes

* **docs:** update documentation and configs ([812ccbe](https://github.com/I-am-PUID-0/DUMB_docs/commit/812ccbe56cee22b01a082b787902043b42ed58dd))
* **master:** release 1.0.1 ([#1](https://github.com/I-am-PUID-0/DUMB_docs/issues/1)) ([88c7c8d](https://github.com/I-am-PUID-0/DUMB_docs/commit/88c7c8d327c3d5ea8aeaa1b05a12fcfa7e2349c1))
* **master:** release 1.1.0 ([#2](https://github.com/I-am-PUID-0/DUMB_docs/issues/2)) ([79599d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/79599d8566b26301637053d6298d161b21daf07d))
* **master:** release 1.2.0 ([#3](https://github.com/I-am-PUID-0/DUMB_docs/issues/3)) ([e5b7bcf](https://github.com/I-am-PUID-0/DUMB_docs/commit/e5b7bcf2f89da59303f762617619d2c5edd4adda))
* **master:** release 1.2.1 ([#4](https://github.com/I-am-PUID-0/DUMB_docs/issues/4)) ([2020204](https://github.com/I-am-PUID-0/DUMB_docs/commit/2020204b527034edd12caf716d473f080a1302cb))
* **master:** release 1.2.2 ([#5](https://github.com/I-am-PUID-0/DUMB_docs/issues/5)) ([977579f](https://github.com/I-am-PUID-0/DUMB_docs/commit/977579ffcafb4d5cc502200c3ef0135ccae2ccb6))
* **master:** release 1.2.3 ([#6](https://github.com/I-am-PUID-0/DUMB_docs/issues/6)) ([c7a6416](https://github.com/I-am-PUID-0/DUMB_docs/commit/c7a64169ab2e92918b6d399f886ab3bc7bc769b1))
* **master:** release 1.2.4 ([#10](https://github.com/I-am-PUID-0/DUMB_docs/issues/10)) ([e55ca5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/e55ca5f48e7a3c5bfe73e26f37950cffc0499993))
* **master:** release 1.3.0 ([#13](https://github.com/I-am-PUID-0/DUMB_docs/issues/13)) ([f599724](https://github.com/I-am-PUID-0/DUMB_docs/commit/f5997249905cb61ebad6f04f633278a7c13b01b7)), closes [#11](https://github.com/I-am-PUID-0/DUMB_docs/issues/11)
* **master:** release 1.3.1 ([#14](https://github.com/I-am-PUID-0/DUMB_docs/issues/14)) ([12131d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/12131d8ba9fb253b8596c42ba3ec30dbe419be44))
* **master:** release 1.3.2 ([#15](https://github.com/I-am-PUID-0/DUMB_docs/issues/15)) ([0c918fd](https://github.com/I-am-PUID-0/DUMB_docs/commit/0c918fd4bec7efe446c201a2bc877cce5e776ee1))
* **master:** release 1.3.3 ([#16](https://github.com/I-am-PUID-0/DUMB_docs/issues/16)) ([d6555d9](https://github.com/I-am-PUID-0/DUMB_docs/commit/d6555d9042efc17cfbc0919325afbb77a9a4b1c4))
* **master:** release 1.3.4 ([#18](https://github.com/I-am-PUID-0/DUMB_docs/issues/18)) ([24ee66f](https://github.com/I-am-PUID-0/DUMB_docs/commit/24ee66fa22c010e8fa242e52ffd41ee71df08989))
* **master:** release 1.3.5 ([#19](https://github.com/I-am-PUID-0/DUMB_docs/issues/19)) ([3312143](https://github.com/I-am-PUID-0/DUMB_docs/commit/33121432966f148e29d765daf54a1d5726bf3c4e))
* **master:** release 1.4.0 ([#21](https://github.com/I-am-PUID-0/DUMB_docs/issues/21)) ([7a5e870](https://github.com/I-am-PUID-0/DUMB_docs/commit/7a5e8703cd178109d659ddd9623d5963020b03af))
* **master:** release 1.5.0 ([#23](https://github.com/I-am-PUID-0/DUMB_docs/issues/23)) ([cb9b73f](https://github.com/I-am-PUID-0/DUMB_docs/commit/cb9b73f3e276ba7bf0293ea57d6641b2cbafc542))
* **master:** release 1.6.0 ([#30](https://github.com/I-am-PUID-0/DUMB_docs/issues/30)) ([74a64b9](https://github.com/I-am-PUID-0/DUMB_docs/commit/74a64b9d7905ada8806677ce0c5576b386504761))


### 📖 Documentation

* Add Decypharr service documentation ([19c8c50](https://github.com/I-am-PUID-0/DUMB_docs/commit/19c8c5078845956d066117b18dd09a6f1042dc21))
* Add guidance for host-based media server mount path consistency ([3babdaf](https://github.com/I-am-PUID-0/DUMB_docs/commit/3babdaf8821af088c6079062fd4a037c25f07a4a))
* **deployment:** update Docker and WSL guides with additional notes for sharing mounts ([f1f6ecf](https://github.com/I-am-PUID-0/DUMB_docs/commit/f1f6ecff1b77c43445d00a7a50b4e330e8616104))
* **docker:** Improves the Docker deployment guide by refining notes and tips for clarity. ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* init push of DUMB docs ([9d59855](https://github.com/I-am-PUID-0/DUMB_docs/commit/9d59855de0c7ff87fb7389863050876888da5a82))
* Update CLI Debrid documentation ([288e49b](https://github.com/I-am-PUID-0/DUMB_docs/commit/288e49b43a2eb394e4fd3f2ed88616a550a587d3)), closes [#12](https://github.com/I-am-PUID-0/DUMB_docs/issues/12)
* update docker.md ([9bd9e5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/9bd9e5ff203709f97d6487cd39520206faa0a7ca))

## [1.6.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.5.0...1.6.0) (2026-01-14)


### ✨ Features

* **banner:** Add custom banner to indicating ongoing migration ([92bad2b](https://github.com/I-am-PUID-0/DUMB_docs/commit/92bad2b1f346b22329abb7e192f847066c7cd0c9))
* **docs:** add Plex Media Server migration instructions and hardware transcoding setup ([d58ad52](https://github.com/I-am-PUID-0/DUMB_docs/commit/d58ad52eb491cf8d1b351283d43215813795a775))
* **docs:** enhance documentation for Plex Media Server integration and configuration ([af5c5c1](https://github.com/I-am-PUID-0/DUMB_docs/commit/af5c5c17b2357b737ac0a982f2b31c985c2a8120))
* update documentation for core services and integrations ([efa285c](https://github.com/I-am-PUID-0/DUMB_docs/commit/efa285ce177981aaf26fd65966879fbb1649ea77))
* uplift docs from mkdocs to zensical ([#22](https://github.com/I-am-PUID-0/DUMB_docs/issues/22)) ([5548ee3](https://github.com/I-am-PUID-0/DUMB_docs/commit/5548ee36a61eb14e83f78db19fcb9e64949d5a6f))


### 🐛 Bug Fixes

* **changelog:** deployment trigger for Changelog updates ([814bbe1](https://github.com/I-am-PUID-0/DUMB_docs/commit/814bbe1de49d863ce9d5ea724c21afb979e7cbac))
* **docs:** correct punctuation in tip regarding mount structure and propagation ([14255b3](https://github.com/I-am-PUID-0/DUMB_docs/commit/14255b3b24c8855f2ece396b4f10f4f5de3bc767))
* **docs:** correct YAML front matter formatting in Services Overview ([64b1885](https://github.com/I-am-PUID-0/DUMB_docs/commit/64b1885058a260cb9e33a98c6af1e1899c425e5a))
* **docs:** update rclone configuration and enhance key descriptions ([5ebc920](https://github.com/I-am-PUID-0/DUMB_docs/commit/5ebc920913bb62b6392843187e2f5bdfdc6e64cc))
* **docs:** update riven_frontend configuration and add origin key description ([8306b07](https://github.com/I-am-PUID-0/DUMB_docs/commit/8306b071bc07e3182dbf4c477ed341c43fd09169))
* **docs:** update troubleshooting tips for hardware transcoding and onboarding process ([e4c8922](https://github.com/I-am-PUID-0/DUMB_docs/commit/e4c89224b093c14154c739021983657dabc6066c))
* **rclone:** corrects link to decypharr page ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* update decypharr ([3c115a3](https://github.com/I-am-PUID-0/DUMB_docs/commit/3c115a3e3c1b70509605042075fc7e0d76374ff1))
* **workflow:** change PR merge strategy to squash for automated changelog updates ([a123926](https://github.com/I-am-PUID-0/DUMB_docs/commit/a12392634aa35be4cc0c0aa31b76a73c08df8b4f))
* **workflow:** improve changelog update logic and user configuration ([01c44fe](https://github.com/I-am-PUID-0/DUMB_docs/commit/01c44feab56c3c2d11540af19244f38100d3826e))
* **workflow:** reorder steps for auto-approval and merging of changelog PRs ([bf2b5a8](https://github.com/I-am-PUID-0/DUMB_docs/commit/bf2b5a81522f310ea963b9fd2a6c50944234c31e))
* **workflow:** replace commit and push logic with pull request creation for changelog updates ([01fcb3c](https://github.com/I-am-PUID-0/DUMB_docs/commit/01fcb3c3d55d786f5e3a5c6396cb2e94a3fc9bdb))
* **workflow:** update condition for extracting pull request number ([86f5d0d](https://github.com/I-am-PUID-0/DUMB_docs/commit/86f5d0df149d72eca62bfd546f6125cbce0af94b))
* **workflow:** update condition for extracting pull request number to ensure valid URL check ([1e33c2f](https://github.com/I-am-PUID-0/DUMB_docs/commit/1e33c2fd54faf9571c8e16cfb8ef719d6f09cb7f))
* **workflow:** update deploy condition to include 'Automated Changelog Update' title ([f70d45f](https://github.com/I-am-PUID-0/DUMB_docs/commit/f70d45ff19cdb262a0d5a26ea4a8342ae226daa2))
* **workflow:** update token for creating pull requests to use GITHUB_TOKEN ([f9a7130](https://github.com/I-am-PUID-0/DUMB_docs/commit/f9a7130290da03ed8db52a699b7ae6051a2f7111))


### 🤡 Other Changes

* **docs:** update documentation and configs ([812ccbe](https://github.com/I-am-PUID-0/DUMB_docs/commit/812ccbe56cee22b01a082b787902043b42ed58dd))
* **master:** release 1.0.1 ([#1](https://github.com/I-am-PUID-0/DUMB_docs/issues/1)) ([88c7c8d](https://github.com/I-am-PUID-0/DUMB_docs/commit/88c7c8d327c3d5ea8aeaa1b05a12fcfa7e2349c1))
* **master:** release 1.1.0 ([#2](https://github.com/I-am-PUID-0/DUMB_docs/issues/2)) ([79599d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/79599d8566b26301637053d6298d161b21daf07d))
* **master:** release 1.2.0 ([#3](https://github.com/I-am-PUID-0/DUMB_docs/issues/3)) ([e5b7bcf](https://github.com/I-am-PUID-0/DUMB_docs/commit/e5b7bcf2f89da59303f762617619d2c5edd4adda))
* **master:** release 1.2.1 ([#4](https://github.com/I-am-PUID-0/DUMB_docs/issues/4)) ([2020204](https://github.com/I-am-PUID-0/DUMB_docs/commit/2020204b527034edd12caf716d473f080a1302cb))
* **master:** release 1.2.2 ([#5](https://github.com/I-am-PUID-0/DUMB_docs/issues/5)) ([977579f](https://github.com/I-am-PUID-0/DUMB_docs/commit/977579ffcafb4d5cc502200c3ef0135ccae2ccb6))
* **master:** release 1.2.3 ([#6](https://github.com/I-am-PUID-0/DUMB_docs/issues/6)) ([c7a6416](https://github.com/I-am-PUID-0/DUMB_docs/commit/c7a64169ab2e92918b6d399f886ab3bc7bc769b1))
* **master:** release 1.2.4 ([#10](https://github.com/I-am-PUID-0/DUMB_docs/issues/10)) ([e55ca5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/e55ca5f48e7a3c5bfe73e26f37950cffc0499993))
* **master:** release 1.3.0 ([#13](https://github.com/I-am-PUID-0/DUMB_docs/issues/13)) ([f599724](https://github.com/I-am-PUID-0/DUMB_docs/commit/f5997249905cb61ebad6f04f633278a7c13b01b7)), closes [#11](https://github.com/I-am-PUID-0/DUMB_docs/issues/11)
* **master:** release 1.3.1 ([#14](https://github.com/I-am-PUID-0/DUMB_docs/issues/14)) ([12131d8](https://github.com/I-am-PUID-0/DUMB_docs/commit/12131d8ba9fb253b8596c42ba3ec30dbe419be44))
* **master:** release 1.3.2 ([#15](https://github.com/I-am-PUID-0/DUMB_docs/issues/15)) ([0c918fd](https://github.com/I-am-PUID-0/DUMB_docs/commit/0c918fd4bec7efe446c201a2bc877cce5e776ee1))
* **master:** release 1.3.3 ([#16](https://github.com/I-am-PUID-0/DUMB_docs/issues/16)) ([d6555d9](https://github.com/I-am-PUID-0/DUMB_docs/commit/d6555d9042efc17cfbc0919325afbb77a9a4b1c4))
* **master:** release 1.3.4 ([#18](https://github.com/I-am-PUID-0/DUMB_docs/issues/18)) ([24ee66f](https://github.com/I-am-PUID-0/DUMB_docs/commit/24ee66fa22c010e8fa242e52ffd41ee71df08989))
* **master:** release 1.3.5 ([#19](https://github.com/I-am-PUID-0/DUMB_docs/issues/19)) ([3312143](https://github.com/I-am-PUID-0/DUMB_docs/commit/33121432966f148e29d765daf54a1d5726bf3c4e))
* **master:** release 1.4.0 ([#21](https://github.com/I-am-PUID-0/DUMB_docs/issues/21)) ([7a5e870](https://github.com/I-am-PUID-0/DUMB_docs/commit/7a5e8703cd178109d659ddd9623d5963020b03af))
* **master:** release 1.5.0 ([#23](https://github.com/I-am-PUID-0/DUMB_docs/issues/23)) ([cb9b73f](https://github.com/I-am-PUID-0/DUMB_docs/commit/cb9b73f3e276ba7bf0293ea57d6641b2cbafc542))


### 📖 Documentation

* Add Decypharr service documentation ([19c8c50](https://github.com/I-am-PUID-0/DUMB_docs/commit/19c8c5078845956d066117b18dd09a6f1042dc21))
* Add guidance for host-based media server mount path consistency ([3babdaf](https://github.com/I-am-PUID-0/DUMB_docs/commit/3babdaf8821af088c6079062fd4a037c25f07a4a))
* **deployment:** update Docker and WSL guides with additional notes for sharing mounts ([f1f6ecf](https://github.com/I-am-PUID-0/DUMB_docs/commit/f1f6ecff1b77c43445d00a7a50b4e330e8616104))
* **docker:** Improves the Docker deployment guide by refining notes and tips for clarity. ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))
* init push of DUMB docs ([9d59855](https://github.com/I-am-PUID-0/DUMB_docs/commit/9d59855de0c7ff87fb7389863050876888da5a82))
* Update CLI Debrid documentation ([288e49b](https://github.com/I-am-PUID-0/DUMB_docs/commit/288e49b43a2eb394e4fd3f2ed88616a550a587d3)), closes [#12](https://github.com/I-am-PUID-0/DUMB_docs/issues/12)
* update docker.md ([9bd9e5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/9bd9e5ff203709f97d6487cd39520206faa0a7ca))

## [1.5.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.4.0...1.5.0) (2026-01-14)


### ✨ Features

* uplift docs from mkdocs to zensical ([#22](https://github.com/I-am-PUID-0/DUMB_docs/issues/22)) ([5548ee3](https://github.com/I-am-PUID-0/DUMB_docs/commit/5548ee36a61eb14e83f78db19fcb9e64949d5a6f))

## [1.4.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.5...1.4.0) (2025-12-30)


### ✨ Features

* update documentation for core services and integrations ([efa285c](https://github.com/I-am-PUID-0/DUMB_docs/commit/efa285ce177981aaf26fd65966879fbb1649ea77))

## [1.3.5](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.4...1.3.5) (2025-08-18)


### 📖 Documentation

* update docker.md ([9bd9e5f](https://github.com/I-am-PUID-0/DUMB_docs/commit/9bd9e5ff203709f97d6487cd39520206faa0a7ca))

## [1.3.4](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.3...1.3.4) (2025-08-17)


### 🐛 Bug Fixes

* update decypharr ([3c115a3](https://github.com/I-am-PUID-0/DUMB_docs/commit/3c115a3e3c1b70509605042075fc7e0d76374ff1))

## [1.3.3](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.2...1.3.3) (2025-07-31)


### 🐛 Bug Fixes

* **docs:** correct punctuation in tip regarding mount structure and propagation ([14255b3](https://github.com/I-am-PUID-0/DUMB_docs/commit/14255b3b24c8855f2ece396b4f10f4f5de3bc767))

## [1.3.2](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.1...1.3.2) (2025-07-31)


### 📖 Documentation

* Add guidance for host-based media server mount path consistency ([3babdaf](https://github.com/I-am-PUID-0/DUMB_docs/commit/3babdaf8821af088c6079062fd4a037c25f07a4a))

## [1.3.1](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.3.0...1.3.1) (2025-07-29)


### 🐛 Bug Fixes

* **rclone:** corrects link to decypharr page ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))


### 📖 Documentation

* **docker:** Improves the Docker deployment guide by refining notes and tips for clarity. ([7e25b02](https://github.com/I-am-PUID-0/DUMB_docs/commit/7e25b021535873697f405d469aa28195b31d7afe))

## [1.3.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.2.4...1.3.0) (2025-07-29)


### ✨ Features

* **docs:** add Plex Media Server migration instructions and hardware transcoding setup ([d58ad52](https://github.com/I-am-PUID-0/DUMB_docs/commit/d58ad52eb491cf8d1b351283d43215813795a775))


### 📖 Documentation

* Update CLI Debrid documentation ([288e49b](https://github.com/I-am-PUID-0/DUMB_docs/commit/288e49b43a2eb394e4fd3f2ed88616a550a587d3)), closes [#12](https://github.com/I-am-PUID-0/DUMB_docs/issues/12)

## [1.2.4](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.2.3...1.2.4) (2025-07-28)


### 🐛 Bug Fixes

* **docs:** update rclone configuration and enhance key descriptions ([5ebc920](https://github.com/I-am-PUID-0/DUMB_docs/commit/5ebc920913bb62b6392843187e2f5bdfdc6e64cc))
* **docs:** update riven_frontend configuration and add origin key description ([8306b07](https://github.com/I-am-PUID-0/DUMB_docs/commit/8306b071bc07e3182dbf4c477ed341c43fd09169))
* **docs:** update troubleshooting tips for hardware transcoding and onboarding process ([e4c8922](https://github.com/I-am-PUID-0/DUMB_docs/commit/e4c89224b093c14154c739021983657dabc6066c))

## [1.2.3](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.2.2...1.2.3) (2025-07-28)


### 🐛 Bug Fixes

* **workflow:** change PR merge strategy to squash for automated changelog updates ([a123926](https://github.com/I-am-PUID-0/DUMB_docs/commit/a12392634aa35be4cc0c0aa31b76a73c08df8b4f))
* **workflow:** improve changelog update logic and user configuration ([01c44fe](https://github.com/I-am-PUID-0/DUMB_docs/commit/01c44feab56c3c2d11540af19244f38100d3826e))
* **workflow:** reorder steps for auto-approval and merging of changelog PRs ([bf2b5a8](https://github.com/I-am-PUID-0/DUMB_docs/commit/bf2b5a81522f310ea963b9fd2a6c50944234c31e))
* **workflow:** replace commit and push logic with pull request creation for changelog updates ([01fcb3c](https://github.com/I-am-PUID-0/DUMB_docs/commit/01fcb3c3d55d786f5e3a5c6396cb2e94a3fc9bdb))
* **workflow:** update condition for extracting pull request number ([86f5d0d](https://github.com/I-am-PUID-0/DUMB_docs/commit/86f5d0df149d72eca62bfd546f6125cbce0af94b))
* **workflow:** update condition for extracting pull request number to ensure valid URL check ([1e33c2f](https://github.com/I-am-PUID-0/DUMB_docs/commit/1e33c2fd54faf9571c8e16cfb8ef719d6f09cb7f))
* **workflow:** update deploy condition to include 'Automated Changelog Update' title ([f70d45f](https://github.com/I-am-PUID-0/DUMB_docs/commit/f70d45ff19cdb262a0d5a26ea4a8342ae226daa2))
* **workflow:** update token for creating pull requests to use GITHUB_TOKEN ([f9a7130](https://github.com/I-am-PUID-0/DUMB_docs/commit/f9a7130290da03ed8db52a699b7ae6051a2f7111))


### 🤡 Other Changes

* **docs:** update documentation and configs ([812ccbe](https://github.com/I-am-PUID-0/DUMB_docs/commit/812ccbe56cee22b01a082b787902043b42ed58dd))

## [1.2.2](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.2.1...1.2.2) (2025-07-24)


### 📖 Documentation

* Add Decypharr service documentation ([19c8c50](https://github.com/I-am-PUID-0/DUMB_docs/commit/19c8c5078845956d066117b18dd09a6f1042dc21))

## [1.2.1](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.2.0...1.2.1) (2025-07-24)


### 📖 Documentation

* **deployment:** update Docker and WSL guides with additional notes for sharing mounts ([f1f6ecf](https://github.com/I-am-PUID-0/DUMB_docs/commit/f1f6ecff1b77c43445d00a7a50b4e330e8616104))

## [1.2.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.1.0...1.2.0) (2025-06-27)


### ✨ Features

* **docs:** enhance documentation for Plex Media Server integration and configuration ([af5c5c1](https://github.com/I-am-PUID-0/DUMB_docs/commit/af5c5c17b2357b737ac0a982f2b31c985c2a8120))


### 🐛 Bug Fixes

* **docs:** correct YAML front matter formatting in Services Overview ([64b1885](https://github.com/I-am-PUID-0/DUMB_docs/commit/64b1885058a260cb9e33a98c6af1e1899c425e5a))

## [1.1.0](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.0.1...1.1.0) (2025-06-27)


### ✨ Features

* **banner:** Add custom banner to indicating ongoing migration ([92bad2b](https://github.com/I-am-PUID-0/DUMB_docs/commit/92bad2b1f346b22329abb7e192f847066c7cd0c9))


### 🐛 Bug Fixes

* **changelog:** deployment trigger for Changelog updates ([814bbe1](https://github.com/I-am-PUID-0/DUMB_docs/commit/814bbe1de49d863ce9d5ea724c21afb979e7cbac))

## [1.0.1](https://github.com/I-am-PUID-0/DUMB_docs/compare/1.0.0...1.0.1) (2025-06-20)


### 📖 Documentation

* init push of DUMB docs ([9d59855](https://github.com/I-am-PUID-0/DUMB_docs/commit/9d59855de0c7ff87fb7389863050876888da5a82))

## Changelog
