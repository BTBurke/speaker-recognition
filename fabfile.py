from fabric.api import *
from fabric.operations import put

def python_base():
    sudo('apt-get -y install build-essential')
    sudo('apt-get -y install python-dev')
    sudo('apt-get -y install python-pip')
    sudo('apt-get -y install python-setuptools')
    sudo('apt-get -y install git-core')
    sudo('pip install nose')


def python_worker():
    sudo('apt-get update')
    sudo('apt-get -y install python-numpy')
    sudo('apt-get -y install python-scipy')
    sudo('apt-get -y install python-matplotlib')
    sudo('apt-get -y install python-imaging')
    sudo('apt-get -y install python-numpy-dev libatlas-dev')

def install_mongo():
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    sudo("echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' >> /etc/apt/sources.list.d/mongo.sources.list")
    sudo('apt-get update')
    sudo('apt-get -y install mongodb-10gen')
    put('./fab/install_mongo/mongodb.conf','/etc/',use_sudo=True)
    sudo('pip install pymongo')
    sudo('pip install mongoengine')
    #sudo('mkdir /data')
    #sudo('mkdir /data/db')
    #sudo('chown -R mongodb:nogroup /data/db')

def install_s3cmd(user='ubuntu'):
    sudo('wget -O- -q http://s3tools.org/repo/deb-all/stable/s3tools.key | apt-key add -')
    sudo('wget -O/etc/apt/sources.list.d/s3tools.list http://s3tools.org/repo/deb-all/stable/s3tools.list')
    sudo('apt-get update')
    sudo('apt-get install s3cmd')
    put('./fab/install_s3cmd/s3cfg','/home/'+user+'/.s3cfg')
    put('./fab/install_s3cmd/s3cfg','/root/.s3cfg',use_sudo=True)

def install_boto():
    sudo('pip install boto')

def install_beanstalkd_andconnector():
    sudo('apt-get -y install libevent-dev') #required by beanstalkd (ver <2.0 as of 4/16/11)
    with cd('/tmp'):
        sudo('wget --no-check-certificate https://github.com/downloads/kr/beanstalkd/beanstalkd-1.4.6.tar.gz')
        sudo('tar xzf beanstalkd-1.4.6.tar.gz')
        with cd('beanstalkd-1.4.6'):
            sudo('./configure')
            sudo('make')
            sudo('mv beanstalkd /usr/bin/beanstalkd')
            sudo('ln -s /usr/bin/beanstalkd /etc/init.d/beanstalkd')
            sudo('update-rc.d beanstalkd defaults')
            sudo('/etc/init.d/beanstalkd -d')
    sudo('pip install pyyaml')
    with cd('/tmp'):
        sudo('git clone git://github.com/earl/beanstalkc.git')
        with cd('beanstalkc'):
            sudo('python setup.py install')

def install_speaker_recognition():
    #Following required for speaker recognition
    sudo('apt-get -y install libsndfile-dev')
    sudo('apt-get -y install libasound2-dev')
    sudo('pip install scikits.audiolab')
    sudo('pip install scikits.learn')
    with cd('/tmp'):
        sudo('wget http://www.irisa.fr/metiss/guig/spro/spro-4.0.1/spro-4.0.1.tar.gz')
        sudo('tar xvzf spro-4.0.1.tar.gz')
        with cd('spro-4.0'):
            sudo('./configure')
            sudo('make')
            sudo('make install')

def install_yaafe(temp='/tmp/yaafe/'):
    sudo('apt-get -y install cmake cmake-curses-gui libargtable2-0 libargtable2-dev libsndfile1 libsndfile1-dev libmpg123-0 libmpg123-dev libfftw3-3 libfftw3-dev liblapack-dev')
    with cd('/tmp'):
        sudo('wget http://sourceforge.net/projects/yaafe/files/yaafe-v0.63.tgz/download')
        sudo('tar xvzf yaafe-v0.63.tgz')
        with cd('yaafe-v0.63'):
            sudo('cmake -DCMAKE_INSTALL_PREFIX=' + temp + ' -DWITH_FFTW3=ON -DWITH_LAPACK=ON -DWITH_SNDFILE=ON -DWITH_MPG123=ON')
            sudo('make')
            sudo('make install')
            sudo('mv /tmp/yaafe/bin/yaafe-engine /usr/local/bin/')
            sudo('mv /tmp/yaafe/lib/*.so /usr/local/lib/')
            sudo('mv /tmp/yaafe/lib/*.0 /usr/local/lib/')
            try:
                sudo('mkdir /usr/local/lib/yaafe/')
            except:
                pass
            sudo('mv ' + temp + 'yaafe_extensions/yaafefeatures.py /usr/local/lib/yaafe/')
            #run('echo export YAAFE_LIB=/usr/local/lib/yaafe >> ~/.bashrc')
            run('echo export LD_LIBRARY_PATH=/usr/local/lib >> ~/.bashrc')
            

def install_clint():
    sudo('pip install clint')

def install_google_protobuf():
    with cd('/tmp'):
        sudo('wget http://protobuf.googlecode.com/files/protobuf-2.4.1.tar.gz')
        sudo('tar xvzf protobuf-2.4.1.tar.gz')
        with cd('protobuf-2.4.1'):
            sudo('./configure')
            sudo('make')
            sudo('make install')

def install_google_snappy():
    with cd('/tmp'):
        sudo('wget http://snappy.googlecode.com/files/snappy-1.0.3.tar.gz')
        sudo('tar xvzf snappy-1.0.3.tar.gz')
        with cd('snappy-1.0.3'):
            sudo('./configure')
            sudo('make')
            sudo('make install')
    sudo('pip install python-snappy')
    
def install_cassandra():
    with cd('/tmp'):
        sudo('wget http://apache.ziply.com//cassandra/0.8.1/apache-cassandra-0.8.1-bin.tar.gz')
        sudo('mkdir /opt/cassandra')
        sudo('tar xvzf apache-cassandra-0.8.1-bin.tar.gz')
        sudo('mv ./apache-cassandra-0.8.1/* /opt/cassandra/')
    put('./fab/cassandra/cassandra.sh', '/etc/init.d/', use_sudo=True)
    sudo('chmod +x /etc/init.d/cassandra.sh')
    sudo('update-rc.d cassandra.sh defaults')
    put('./fab/cassandra/cassandra-cli','/usr/local/bin/', use_sudo=True)
    sudo('chmod +x /usr/local/bin/cassandra-cli')
    sudo('pip install pycassa')
    
def install_celery():
    sudo('apt-get -y install rabbitmq-server')
    #Add RabbitMQ user=xemplar pwd=xemplar1, set up virtual host, and allow access
    sudo('rabbitmqctl add_user xemplar xemplar1')
    sudo('rabbitmqctl add_vhost xbxvhost')
    sudo('rabbitmqctl set_permissions -p xbxvhost xemplar ".*" ".*" ".*"')
    #TODO: May need to set hostname here in order for RabbitMQ to run correctly
    #      and add alias to /etc/hosts, may be important for EC2 when IP in FQDN
    
    # Need to upgrade to python-dateutil >=1.5 before installing celery
    with cd('/tmp'):
        sudo('wget http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz')
        sudo('tar xvzf python-dateutil-1.5.tar.gz')
        with cd('python-dateutil-1.5'):
            sudo('python setup.py install')
    sudo('pip install celery')
    
def install_monitoring():
    #Install scales from Greplin, push stats to Graphite
    with cd('/tmp'):
        sudo('git clone https://github.com/Greplin/scales')
        with cd('scales'):
            sudo('python setup.py install')
    #Install graphite w/ Django for process monitoring
    sudo('apt-get -y install apache2 libapache2-mod-wsgi')
    sudo('apt-get -y install python-twisted python-cairo python-cairo-dev libcairo2-dev')
    with cd('/tmp'):
        sudo('wget http://www.cairographics.org/releases/pycairo-1.8.8.tar.gz')
        sudo('tar xvzf pycairo-1.8.8.tar.gz')
        with cd('pycairo-1.8.8'):
            sudo('python setup.py install')
    sudo('pip install django')
    sudo('pip install django-tagging')
    sudo('apt-get -y install memcached python-memcache')
    with cd('/tmp'):
        sudo('wget http://launchpad.net/txamqp/trunk/0.3/+download/python-txamqp_0.3.orig.tar.gz')
        sudo('tar xvzf python-txamqp_0.3.orig.tar.gz')
        with cd('python-txamqp-0.3'):
            sudo('python setup.py install')    

def install_neo4j():
    sudo('apt-get -y install python-jpype')
    sudo('pip install neo4j-embedded')

def install_riak():
    with cd('/tmp'):
        sudo('wget http://downloads.basho.com/riak/riak-1.0.1/riak_1.0.1-1_amd64.deb')
        sudo('dpkg -i riak_1.0.1-1_amd64.deb')
        install_google_protobuf()
        sudo('git clone https://github.com/basho/riak-python-client.git')
        with cd('riak-python-client'):
            sudo('python setup.py install')

#------------Roles----------------------------

#Integrated worker installation with resident database
def full_install():
    
    python_base()
    python_worker()
    install_mongo()
    #install_s3cmd()
    install_boto()
    #install_beanstalkd_andconnector()
    install_speaker_recognition()
    install_clint()
    #install_google_protobuf()
    install_google_snappy()
    #install_cassandra()
    #install_yaafe()
    install_celery()
    run('export PYTHONPATH=/home/btb/project/src >> ~/.bashrc')