##################################################################################
#  Main makefile for XOS.
#
#  Use this makefile for generating the docker containers and running docker images for XOS
#
################################
# The following variables can be modified to build alternative images/containers so
# that a single docker engine can run multiple instances of different XOS instances
#
# Note: Override these on the 'make' command line, you do not have to edit this file.

# The docker image prefix
export IMAGE_PREFIX?=xosproject

# The container name prefix (use something like chip- to customize)
export CONTAINER_PREFIX?=

# The next are provided on the container 'run' command line as --add-host parameters
# For various OpenStack servers
# OS_CONTROLLER_IP -> IP Address of the OpenStack Controller
# OS_COMPUTE_NODES -> Comma separated compute node name/IP Address list of all compute nodes

export SQL_PORT_NUMBER?=5432
export OS_CONTROLLER_IP=10.17.173.1
export DB_HOST=xos-database
export OS_COMPUTE_NODES=os10-compute01.test.adtran.com/10.17.173.1

#######################################################################
# DO NOT CHANGE ANY OF THE FOLLOWING UNLESS YOU KNOW WHAT YOU ARE DOING
#
export CERTS?=/usr/local/share/ca-certificates:/usr/local/share/ca-certificates:ro
export DB_CONTAINER_SUFFIX:=xos-db-postgres
BASE_CONTAINERS:=postgresql xos synchronizer

all: usage
	@echo "So, what do you want to do.."

.PHONY: usage
usage:
	@echo ""
	@echo "This Makefile will build and run all of the XOS images and containers for"
	@echo "the CORD application.  The setting up of the OpenStack site within XOS"
	@echo "is still a manual procedure as well as running the TOSCA file to create"
	@echo "your initial configuration."
	@echo ""
	@echo "Allowed targets at this time are:"
	@echo "   make CORD        to make and run the base XOS and Adtran CORD images/containers"
	@echo "   make xos-base    to make and run the base XOS images/containers"
	@echo "   make adCORD      to make and run the Adtran CORD images/containers"
	@echo ""
	@echo "   make clean-all   to fully scrub the XOS VM and related OpenStack objects"
	@echo "   make clean-vaos  to scrub vaos up and ready it to be built again"
	@echo ""
	@echo "  NOTE: The image/container make dependencies are not supported. To 'remake'"
	@echo "        you will need to either do a make 'clean' command or manually execute"
	@echo "        the docker 'rm'; or 'rmi' command as appropriate."
	@echo ""
	@echo "The 'base' XOS images and container targets are: postgresql, xos, and synchronizer"
	@echo "and you can building images by appending build- to the base name or run the"
	@echo "containers by appending run- to the base name such as:"
	@echo ""
	@echo "    make build-xos"
	@echo "    make run-synchronizer"
	@echo ""
	@echo "  NOTE : All these are experimental and may not yet be implemented fully."
	@echo ""
	@echo "==========================================================================="
	@echo "To customize your image or container names, override the following variables:"
	@echo ""
	@echo "   IMAGE_PREFIX     - Docker image name prefix, currently '${IMAGE_PREFIX}'"
	@echo "   CONTAINER_PREFIX - Docker image name prefix, currently '${CONTAINER_PREFIX}'"
	@echo ""
	@echo "--------------------"
	@echo ""
	@echo "The next are provided on the container 'run' command line as --add-host parameters"
	@echo "For various Database and OpenStack servers"
	@echo ""
	@echo "   OS_CONTROLLER_IP - OpenStack controller , currently '${OS_CONTROLLER_IP}'"
	@echo "   OS_COMPUTE_NODES - Comma separated compute node name/IP Address list of all compute nodes, currently '${OS_COMPUTE_NODES}'"
	@echo ""

######################################################################################

PHONY: CORD
CORD: xos-base adCORD
	@echo "Done"

PHONY: xos-base
xos-base: build-base run-base
	@echo "All base XOS images have been built and are now running"

PHONY: run-base
run-base: build-base
	@for container in ${BASE_CONTAINERS}; do	\
		make -f Makefile.adtn -C containers/$$container run;		\
	done
	@echo "** All base XOS images are now running"

PHONY: build-base
build-base:
	@for container in ${BASE_CONTAINERS}; do	\
		make -f Makefile.adtn -C containers/$$container build;	\
	done
	@echo "** All base XOS images have been built"

PHONY: adCORD
adCORD: build-adCORD run-adCORD
	@echo "** All base adCORD images have been built and are running"

PHONY: run-adCORD
run-adCORD:
	make -f Makefile.adtn -C xos/configurations/adCord run

PHONY: build-adCORD
build-adCORD:
	make -f Makefile -C xos/configurations/adtn-cord build

######################################################################################
# Start /. Stop

PHONY: stop
stop:
	@echo "NOTE: Expect a 10 second timeout per container being stopped..."
	@echo ""
	make -f Makefile.adtn -C xos/configurations/adCord stop
	@for container in ${BASE_CONTAINERS}; do	\
		make -f Makefile.adtn -C containers/$$container stop;	\
	done

PHONY: start
start:
	@for container in ${BASE_CONTAINERS}; do	\
		make -f Makefile.adtn -C containers/$$container start;	\
	done
	make -f Makefile.adtn -C xos/configurations/adCord start

######################################################################################
# Cleanup

.PHONY: clean
clean: clean-containers clean-images
	@echo "Clean complete"

.PHONY: clean-images
clean-images: clean-containers
	@for container in ${BASE_CONTAINERS}; do		\
		make -f Makefile.adtn -C containers/$$container clean-image;	\
	done
	make -f Makefile.adtn -C xos/configurations/adCord clean-image
	@echo "** Clean of XOS docker images complete"

.PHONY: clean-containers
clean-containers:
	@for container in ${BASE_CONTAINERS}; do			\
		make -f Makefile.adtn -C containers/$$container clean-container;	\
	done
	make -f Makefile.adtn -C xos/configurations/adCord clean-container
	@echo "** Clean running XOS containers complete"
