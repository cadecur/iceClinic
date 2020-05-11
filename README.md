# iceClinic

## Introduction
This is a Bokeh Server webapp made for Ice911 Research to better display the results of their climate models. This webapp uses the geoviews extension of holoviews to create the geographical visualizations.

## Set-Up
First, install the necessary dependencies, its recommended you do this in a virtual environment
```
conda create -n env-name -c pyviz -c conda-forge geoviews holoviews bokeh xarray cartopy cftime
conda activate env-name
```
Its recommend that you use conda to install and manage the packages. Geoviews has issues with pip that were throwing low-level dependency errors (as of 5/11/20).

Next, pull the repo and create a data subdirectory. In that directory add the following 12 files from the google drive. 
```
f09_g16.B.cobalt.CONTROL.MAY.FWI.200005-208106.nc
f09_g16.B.cobalt.CONTROL.MAY.PRECT.200005-208106.nc
f09_g16.B.cobalt.CONTROL.MAY.SPI.200005-208106.nc
f09_g16.B.cobalt.CONTROL.MAY.TS.200005-208106.nc
f09_g16.B.cobalt.FRAM.MAY.FWI.200005-208106.nc
f09_g16.B.cobalt.FRAM.MAY.PRECT.200005-208106.nc
f09_g16.B.cobalt.FRAM.MAY.SPI.200005-208106.nc
f09_g16.B.cobalt.FRAM.MAY.TS.200005-208106.nc
f09_g16.B.cobalt.GLOBAL.MAY.FWI.200005-208106.nc
f09_g16.B.cobalt.GLOBAL.MAY.PRECT.200005-208106.nc
f09_g16.B.cobalt.GLOBAL.MAY.SPI.200005-208106.nc
f09_g16.B.cobalt.GLOBAL.MAY.TS.200005-208106.nc
```
Additionally, you can use files of your own containing any variables and any intervention. The files must adhere to the netCDF4 convention and relevant constants in the main.py must be changed to accomodate those files.

Now you can run the app locally with the following commands. You must run this command from the parent directory of the git repo.
```
bokeh serve .\iceClinic\
```

## Deployment
The current manner used to deploy this webapp is to pull the repo inside of an AWS EC2 instance, start and run the bokeh server in a screen, and access the running process using the public DNS of the instance.

First, select an EC2 instance. The team used a t2.medium with an attached 8GB of EBS storage. Additionally, a security group was created to allow all incoming traffic to access port 5006 on the instance. Next, ssh into the instance and perform the set-up steps in the previous section. A convientent way to get the datafiles to create a folder in a s3 bucket and use the AWS CLI to sync that s3 folder with the local 'data' directory.

Lastly, to start the bokeh server in the ec2 instance, use the following command in the parent directory of the github repo.
```
bokeh serve --allow-websocket-origin=ec2-54-186-39-140.us-west-2.compute.amazonaws.com:5006 --num-procs 0 iceClinic
```
The argument allow-websocket-origin allows access to the server using the public DNS and the num-procs 0 argument a bokeh server process for each core that the instance's CPU has. Torando, the library that Bokeh server runs on, will automatically load balance among these running processes. 
