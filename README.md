# AntiSLAPP

AntiSLAPP is an open source legal defender that can assist an individual with 
putting together a defence against a defamation lawsuit in Canadian jurisdiction.

Antislapp runs as a guided conversation, asking the user questions. When the questions have 
been answered, the AI provides the user with two documents: 
  1. A statement of defence for you, the user.  This is to serve as a starting point for the user's defence.
  2. A supplemental document explaining the steps involved in a civil suit. 

It is currently live at [https://antislapp.ca](https://antislapp.ca)


## Installation / Development

The dev branch is live at [https://antislapp.ca/dev](https://antislapp.ca/dev), but is not guaranteed to be up to date or bug-free.

To run your own copy of AntiSLAPP you need a public-facing webserver serving https requests, and an account (A Google account) on dialogflow.com.  The architecture is Browser-->Chat Server-->Dialogflow.com-->Fulfillment Server.

The Chat Server portion can be run on localhost provided you have exported an environment variable called "CLIENT_ACCESS_TOKEN" with the matching value from your Dialogflow agent settings.  The Fulfillment Server needs to be able to serve public secure requests from Dialogflow.com.


### Dialogflow setup

1. Create a new agent. Lets call it *MyAgent*.
1. Go to the agent setup page, and the "Export and Import" tab.
    1. This repo includes a zip file at the top level. Download that zip file.
    1. Choose "RESTORE FROM ZIP" and follow the instructions to upload the zip file you just downloaded into DialogFlow.
1. On the "General" tab of the agent setup page, there is a field labeled "Client access token"  You will need this later.
1. Using the page navigation on DialogFlow, go to the Fulfillment page.
    1. Replace the URL field with your website address and the /fulfill page.
    1. Example:  https://mysite.com/fulfill
1. You're good to go on the dialogflow side!

### Server setup

The server side needs to serve the python files.  Several options are available such as apache with mod-wsgi or nginx and fast-cgi. This readme will describe setting up nginx on a clean ubuntu image.  Some of these steps may be unnecessary for you.

1. Install nginx server:
    1. `sudo apt install nginx`
1. Install pip (for python packages)
    1. `sudo apt install python-pip`
    1. `sudo pip install --upgrade pip`
1. Install python package flup (allows fast-cgi to work with python wsgi)
    1. `sudo pip install flup`
1. Install fcgi (fast-cgi for nginx)
    1. `sudo apt install spawn-fcgi`
1. Your webserver should show the NGINX default page now on http. You may need to start the services or reboot.
1. Install AntiSLAPP repo
    1. `cd /var/www`
    1. `sudo git clone https://github.com/riolet/antislapp.git`
    1. `chown -R www-data: /var/www/antislapp`
    1. `sudo pip install -r /var/www/antislapp/requirements.txt`
1. Site configuration. Https is necessary but full site configuration is beyond the scope of these instructions. Make sure your site includes the following:
    1. Note the CLIENT_ACCESS_TOKEN parameter below. You will need to replace that with your own token, from your dialogflow agent settings.
```
location / {
    root /var/www/antislapp/antislapp;
    fastcgi_param REQUEST_METHOD $request_method;
    fastcgi_param QUERY_STRING $query_string;
    fastcgi_param CONTENT_TYPE $content_type;
    fastcgi_param CONTENT_LENGTH $content_length;
    fastcgi_param GATEWAY_INTERFACE CGI/1.1;
    fastcgi_param SERVER_SOFTWARE nginx/$nginx_version;
    fastcgi_param REMOTE_ADDR $remote_addr;
    fastcgi_param REMOTE_PORT $remote_port;
    fastcgi_param SERVER_ADDR $server_addr;
    fastcgi_param SERVER_PORT $server_port;
    fastcgi_param SERVER_NAME $server_name;
    fastcgi_param SERVER_PROTOCOL $server_protocol;
    fastcgi_param SCRIPT_FILENAME $fastcgi_script_name;
    fastcgi_param PATH_INFO $fastcgi_script_name;
    fastcgi_param CLIENT_ACCESS_TOKEN "<your token here>";
    fastcgi_pass 127.0.0.1:9002;
}
location /static/ {
    root /var/www/antislapp/antislapp;
    if (-f $request_filename) {
        rewrite ^/static/(.*)$ /static/$1 break;
    }
}
``` 
8. reload nginx and start up fcgi
    1. `sudo nginx -s reload` To enable your site
    1. `spawn-fcgi -d /var/www/antislapp/antislapp -f /var/www/antislapp/antislapp/index.py -a 127.0.0.1 -p 9002` To enable fcgi to run your python scripts
9. Your website should be good to go now. Make sure it works if you connect at http**s**://&lt;your-site&gt;.com
