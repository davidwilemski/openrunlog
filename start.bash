source /home/david/orl_env/bin/activate
source /home/david/.bash_profile
supervisord --nodaemon --configuration /home/david/orl/supervisord.conf --user=david
