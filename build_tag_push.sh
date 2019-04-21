git clone --depth 1 -b master https://github.com/MVPStudio/build_setup.git ~/build_setup
ls -l ~/build_setup
sudo pip install -r ~/build_setup/requirements.txt
python ~/build_setup/build_tag_push.py