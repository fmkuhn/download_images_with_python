#!/usr/bin/env python

import getopt #get command line parameters
import urllib #for image downloading
import os #operating system stuff, like path
import sys #Unexpected errors

## This downloads a list of images (given as a list of URLs in a file), saving each of them in a directory according to the server structure it was on below the directory this script is run in.
# @param inputfile A file containing a list of URLs, one in each line.
# @param reload_all Reload all images, even if they already exist (Default: False)
# @param error_filename (optional) A file for logging potential error messages (Default: 'errors.log').
def download_images(inputfile, reload_all = False, error_filename = 'errors.log'):
    try:
        with open(inputfile, 'r') as url_list, open(error_filename, 'w') as error_file: #open images_filename for reading url_list and error_file for logging errors, 'with' makes sure the files get closed no matter what
            error_count = 0
            for url in url_list:
                if not url: continue #ignore empty lines
                error_count += download(url, error_file, reload_all)
                print('') #Better readable output

            print ('Finished downloading images.')
            if error_count > 0:
                print('There were', error_count, 'errors, check \'' + error_filename + '\'')
    except IOError as error:
        print(str(error))
        raise

## Downloads a single image to the disk.
# @param url The URL where the image is located.
# @param error_file The file errors are logged to.
# @param reload_all Determines if 
# @return integer - 1 if an error occurred (thus increasing error_count), 0 otherwise
def download(url, error_file, reload_all):
    url = url.rstrip() #remove line end from end of url
    print (url, '...')
    local_image_path = url.split('//')[-1] #ignore everything before //, e.g. http:, the rest is the local image path, where each item between two '/' is a subdirectory and the last item is the filename
    if not reload_all and os.path.exists(local_image_path):
        print ('...is already present at \'' + local_image_path + '\' - Continuing with next url')
        return 0 #continue without error
    try:
        image = urllib.request.urlopen(url) #try opening url
        if not create_subdirectories(local_image_path): #creating subdirectories failed
            return 1
        with open(local_image_path, 'wb') as local_image: #open local_image_path as local_image for writing the contents of the url, 'with' makes sure the file gets closed no matter what
            try:
                local_image.write(image.read()) #writes image from url to disk
            except:
                log_error(error_file, local_image_path, 'Could not write image to disk : ' + sys.exc_info()[0])
                return 1
        print ('...successfully saved to \'' + local_image_path + '\'')
    except urllib2.URLError as error: #an error occurred while trying to reach url
        log_error(error_file, local_image_path, str(error))
        return 1
    except KeyboardInterrupt: #catch keyboard interrupt, since all other errors are passed below
        raise
    except: #catch all other exceptions
        log_error(error_file, local_image_path, 'Unexpected error - ' + str(sys.exc_info()[0]))
        return 1
    return 0
    
## Creates missing subdirectories for local_image_path
# @param local_image_path Local path to the image file including subdirectories
# @return boolean - False if an error occurred, True otherwise
def create_subdirectories(local_image_path):
    current_directory = os.path.abspath('.') #save current path
    directory_list = local_image_path.split('/')[:-1] #ignore last item, i.e., the filename
    for directory in directory_list:
        if not os.path.exists(directory): #directory does not exist
            try:
                os.mkdir(directory) #create directory
            except:
                log_error(error_file, local_image_filename, 'Could not create ' + directory + ' - ' + sys.exc_info()[0])
                return False
        elif not os.path.isdir(directory): #exists, but is no directory -->
            log_error(error_file, local_image_filename, directory + ' exists, but is no directory!')
            return False
        os.chdir(directory) #change into directory
        
    os.chdir(current_directory) #change back into directory where the script is run
    return True

## Logs error to error_file and console.
# @param error_file File, where errors are logged to.
# @param error_string String to log to error_file and console
def log_error(error_file, local_image_filename, error_string):
    print (error_string)
    error_file.write(local_image_filename + ' -- ' + error_string + '\n\n') # add new lines for better readability

## Printing script usage to the console
# @param script_name Name of this script from command line parameters
def print_usage(script_name):
    print(script_name, '-i <imagefile> [-e <errorfile> -r]')
    print('')
    print('Options:')
    print('  -h, --help                      Show this help')
    print('  -i, --imagefile <filename>      File containing image URLs')
    print('  -e, --errorfile <filename>      File for writing error log')
    print('  -r, --reload                    Reload all images')

## Main function when download_images is called as a script, i.e., './download_images.py ...'
# @param argv command line parameter list
def main(argv):
    inputfile = '' #see download_images doc
    error_filename = 'errors.log' #see download_images doc
    reload_all = False #see download_images doc
    try:
        opts, args = getopt.getopt(argv,'hi:e:r',['help','inputfile=','errorfile=','reload']) #get options and arguments
    except getopt.GetoptError as error: #unknown parameter or missing argument for parameter
        print(str(error))
        print_usage(argv[0])
        sys.exit(2) #exit with error
    for opt, arg in opts:
        if opt in ('-h', '--help'): #help called
            print_usage(sys.argv[0])
            sys.exit() #exit without error
        elif opt in ('-i', '--inputfile'): #inputfile filename found
            inputfile = arg
        elif opt in ('-e', '--errorfile'): #errorfile filename found
            error_filename = arg
        elif opt in ('-r', '--reload'):
            reload_all = True
    if not inputfile: #-i [--imagefile] is mandatory
        print('Missing option -i')
        print_usage(sys.argv[0])
        sys.exit(2)

    download_images(inputfile, reload_all, error_filename)

if __name__ == '__main__':
    main(sys.argv[1:])
