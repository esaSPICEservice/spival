from os import remove, path

def kernel_extension2type(kernel_extension):
    kernel_type_map = {
        "TI": "IK",
        "TF": "FK",
        "TM": "MK",
        "TSC": "SCLK",
        "TLS": "LSK",
        "TPC": "PCK",
        "BC": "CK",
        "BSP": "SPK",
        "BPC": "PCK",
        "BDS": "DSK"
    }

    try:
        kernel_type = kernel_type_map[kernel_extension]
    except:
        print('Kernel Extension {} not recognised'.format(kernel_extension))
        kernel_type = ''

    return kernel_type


def kernel_type(kernel):

    try:
        kernel_extension = kernel.split('.')[1]
        kernel_type = kernel_extension2type(kernel_extension.upper()).lower()
    except:
        print('Kernel has no extension')
        kernel_type = ''

    return kernel_type


def fill_template(template,
                  file,
                  replacements,
                  cleanup=False):


   #
   # If the temp   late file is equal to the output file then we need to create a temporary template - which will be
   # a duplicate - in order to write in the file. A situation where we would like to have them be the same is
   # for example if we call this function several times in a row, replacing keywords in the template in steps
   #
   if template == file:
       with open(file, 'r') as f:
           with open('fill_template.temp', "w+") as t:
               for line in f:
                   t.write(line)

       template = 'fill_template.temp'


   with open(file, "w+") as f:
       #
       # Items are replaced as per correspondance in between the replacements dictionary
       #
       with open(template, 'r') as t:
           for line in t:
               if '{' in line:
                   for k, v in replacements.items():
                       if '{' + k + '}' in line: line = line.replace('{' + k + '}', v)
               f.write(line)

               #
               # If the option cleanup is set as true, we remove the keyword assignments in the filled templated which are
               # unfilled (they should be optional)
               #
   if cleanup:

       with open(file, 'r') as f:
           with open('fill_template.temp', 'w+') as t:
               for line in f:
                   t.write(line)

       template = 'fill_template.temp'

       with open(file, 'w+') as f:
           with open('fill_template.temp', 'r') as t:
               for line in t:
                   if '{' not in line:
                       f.write(line)

                       #
                       # The temporary files are removed
                       #
   if path.isfile('fill_template.temp'):
       remove('fill_template.temp')