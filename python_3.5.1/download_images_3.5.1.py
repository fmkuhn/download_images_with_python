#!/usr/bin/env python3

import getopt #get command line parameters
import urllib.request #downloading images
import urllib.error #handling errors when downloading an image
import os #operating system stuff, like path
import sys #For unexpected errors

## This downloads a list of images (given as a list of URLs in a file). The file may contain empty lines and lines starting with a '#', i.e., comments.
#
# It saves each of them in a directory (according to the server's structure the images was on) below the directory this script is run in,
# e.g., 'http://www.foo.de/bar/xyz.jpg' would be saved in './www.foo.de/bar/xyz.jpg'.
# @param inputfile A file containing a list of URLs, one in each line.
# @param reload_all True = (optional) Reload all images, even if they already exist (Default: False).
# @param error_filename (optional) A file for logging potential error messages (Default: 'errors.log').
# @param number_of_urls (optional) The number of URLs to be downloaded. If this is 0, it was not counted and is therefore not printed in the output
def download_images(inputfile, reload_all = False, error_filename = 'errors.log', number_of_urls = 0):
    try:
        with open(inputfile, 'r') as url_list, open(error_filename, 'w') as error_file: #open images_filename for reading url_list and error_file for logging errors, 'with' makes sure the files get closed no matter what
            error_count = 0
            url_count = 1
            for url in url_list:
                url = url.rstrip() #remove line end as well as spaces from end of url
                if not url or url.startswith('#'):
                    continue #ignore empty lines and lines beginning with a '#'
                if number_of_urls: #number of urls known --> print as part of output
                    print(url_count, '/', number_of_urls, ':', url, '...')
                else:
                    print(url_count, ':', url, '...')
                error_count += download(url, error_file, reload_all)
                url_count +=1
                print('') #Better readable output

            print ('Finished downloading images.')
            if error_count > 0:
                print('There were', error_count, 'errors, check \'' + error_filename + '\'')
    except IOError as error:
        print(str(error))
        raise
    except: #catch all other exceptions
        print('Unexpected error - ' + str(sys.exc_info()[0]))
        raise

## Downloads a single image to the disk.
# @param url The URL where the image is located.
# @param error_file The file errors are logged to.
# @param reload_all True = Reload all images, even if they already exist.
# @return integer - 1 if an error occurred (thus increasing error_count), 0 otherwise.
def download(url, error_file, reload_all):
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
    except urllib.error.URLError as error: #an error occurred while trying to reach url
        log_error(error_file, url, str(error))
        return 1
    except KeyboardInterrupt: #catch keyboard interrupt, since all other errors are only logged and not raised below
        raise
    except: #catch all other exceptions
        log_error(error_file, url, 'Unexpected error - ' + str(sys.exc_info()[0]))
        return 1
    return 0
    
## Creates missing subdirectories for local_image_path.
# @param local_image_path Local path to the image file including subdirectories.
# @return boolean - False if an error occurred, True otherwise.
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
# @param error_causer Url or local filename for which the error occurred
# @param error_string String to log to error_file and console.
def log_error(error_file, error_causer, error_string):
    print(error_string)
    error_file.write(error_causer + ' -- ' + error_string + '\n\n') # add new lines for better readability

## Counts number of lines in the file, which are not empty and don't start with a '#'
# @param inputfilename Name of the file.
# @return integer
def get_number_of_urls(inputfilename):
    try:
        with open(inputfilename, 'r') as f:
            line_counter = 0
            for line in f:
                if not line.strip() or line.startswith('#'):
                    continue
                line_counter += 1
            return line_counter
    except IOError as error:
        print(str(error))
        raise
    except: #catch all other exceptions
        print('Unexpected error - ' + str(sys.exc_info()[0]))
        raise

## Main function when download_images is called as a script, i.e., './download_images.py ...'
# @param argv command line parameter list
def main(argv):
    inputfile = '' #see download_images doc
    error_filename = 'errors.log' #see download_images doc
    reload_all = False #see download_images doc
    disable_linecount = False #If true, the number of lines in inputfile are not read
    number_of_urls = 0 #number of urls
    try:
        opts, args = getopt.getopt(argv,'hi:e:rd',['help','inputfile=','errorfile=','reload','disable-linecount']) #get options and arguments
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
        elif opt in ('-d', '--disable-linecount'):
            disable_linecount = True
    if not inputfile: #-i [--imagefile] is mandatory
        print('Missing option -i')
        print_usage(sys.argv[0])
        sys.exit(2)
    if not disable_linecount:
        number_of_urls = get_number_of_urls(input_filename)
        if not number_of_urls:
            print input_filename, 'does not contain valid lines (lines with a starting \'#\' are ignored)'
            sys.exit(2)
    download_images(inputfile, reload_all, error_filename, number_of_urls)

## Printing script usage to the console
# @param script_name Name of this script from command line parameters
def print_usage(script_name):
    print('Usage:', script_name.split('/')[-1], '-i <imagefile> [-e <errorfile> -r]') #show only filename, not path, on usage
    print('')
    print('Options:')
    print('  -h, --help                      Show this help')
    print('  -i, --imagefile <filename>      File containing image URLs')
    print('  -e, --errorfile <filename>      File for writing error log')
    print('  -r, --reload                    Reload all images')
    print('  -d, --disable-linecount         Do not count number of urls in inputfile')


# Checks if download_images.py is run from the command line or if it is used
if __name__ == '__main__':
    main(sys.argv[1:])
