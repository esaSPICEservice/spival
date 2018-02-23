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