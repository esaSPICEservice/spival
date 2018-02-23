KPL/MK

Meta-kernel for ExoMars 2016 Dataset v210 -- Operational 20180221_002
==========================================================================

   This meta-kernel lists the ExoMars2016 Operational SPICE kernels
   providing information for the full mission based on predicted, test
   and/or measured data.

   The kernels listed in this meta-kernel and the order in which
   they are listed are picked to provide the best data available and
   the most complete coverage for the ExoMars2016 Operational scenario.


Usage of the Meta-kernel
-------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make use
   of this kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool". The SPICELIB
   routine FURNSH loads a kernel into the pool.

   The kernels listed below can be obtained from the ESA SPICE FTP server:

      ftp://spiftp.esac.esa.int/data/SPICE/ExoMars2016/kernels/


Implementation Notes
-------------------------------------------------------------------------

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the ExoMars2016 SPICE data set's ``data'' directory on
   their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.


-------------------

   This file was created on February 21, 2018 by Marc Costa Sitja ESA/ESAC.


   \begindata

     PATH_VALUES       = ( '/Users/mcosta/ExoMars2016/kernels' )

     PATH_SYMBOLS      = ( 'KERNELS' )

     KERNELS_TO_LOAD   = (
                           '$KERNELS/ck/em16_tgo_sc_slt_npo_20180101_20181231_s20170201_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_fpp_015_01_20160314_20170315_s20170201_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_fpp_d170207_pointing_20170305_20170309_s20170201_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_fsp_001_01_20180222_20180228_s20180215_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170301_20170331_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170401_20170430_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170501_20170531_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170601_20170630_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170701_20170731_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170801_20170831_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20170901_20170930_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171001_20171008_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171009_20171013_s20171007_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171014_20171022_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171023_20171028_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171030_20171105_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171106_20171112_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171113_20171119_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171120_20171125_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171127_20171203_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171204_20171210_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171210_20171216_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20171217_20171231_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180101_20180107_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180106_20180114_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180115_20180121_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180115_20180121_s20180204_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180121_20180128_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180121_20180128_s20180204_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180128_20180128_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180128_20180204_s20180204_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180129_20180203_s20171024_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180204_20180211_s20180204_v01.bc'
                           '$KERNELS/ck/em16_tgo_sc_sam_20180211_20180218_s20180215_v01.bc'
                           '$KERNELS/ck/em16_tgo_acs_sop_default_20160314_21000101_s20160719_v01.bc'
                           '$KERNELS/ck/em16_tgo_cassis_scp_tel_20160314_20161019_s20160414_v01.bc'
                           '$KERNELS/ck/em16_tgo_cassis_ipp_tel_20160407_20170309_s20170116_v02.bc'
                           '$KERNELS/ck/em16_tgo_nomad_sop_default_20160404_21000101_s20160719_v01.bc'
                           '$KERNELS/ck/em16_tgo_nomad_scp_20160404_20161019_s20160414_v01.bc'
                           '$KERNELS/ck/em16_edm_sop_axis_20161016_20161019_f20160921_v01.bc'
                           '$KERNELS/ck/em16_edm_sop_spin_20161016_20161019_f20160921_v01.bc'

                           '$KERNELS/fk/em16_tgo_v12.tf'
                           '$KERNELS/fk/em16_edm_v01.tf'
                           '$KERNELS/fk/em16_tgo_ops_v02.tf'
                           '$KERNELS/fk/rssd0002.tf'

                           '$KERNELS/ik/em16_tgo_acs_v05.ti'
                           '$KERNELS/ik/em16_tgo_cassis_v06.ti'
                           '$KERNELS/ik/em16_tgo_frend_v05.ti'
                           '$KERNELS/ik/em16_tgo_nomad_v04.ti'
                           '$KERNELS/ik/em16_edm_deca_v00.ti'

                           '$KERNELS/lsk/naif0012.tls'

                           '$KERNELS/pck/pck00010.tpc'
                           '$KERNELS/pck/de-403-masses.tpc'

                           '$KERNELS/sclk/em16_tgo_step_20180215.tsc'
                           '$KERNELS/sclk/em16_edm_fict_20160921.tsc'

                           '$KERNELS/spk/em16_tgo_flp_006_01_20160314_20210329_v01.bsp'
                           '$KERNELS/spk/em16_tgo_fsp_001_01_20160314_20180312_v01.bsp'
                           '$KERNELS/spk/em16_edm_sot_landing_site_20161020_21000101_v01.bsp'
                           '$KERNELS/spk/em16_edm_fpd_028_01_20161016_20161020_v01.bsp'
                           '$KERNELS/spk/em16_edm_fpd_d161018_postsep_20161016_20161019_v01.bsp'
                           '$KERNELS/spk/de432s.bsp'
                           '$KERNELS/spk/mar097.bsp'

                         )

   \begintext


SPICE Kernel Dataset Version
------------------------------------------------------------------------

   The version of this SPICE Kernel Dataset is provided by the following
   keyword:

   \begindata

      SKD_VERSION = 'v210_20180221_002'

   \begintext


Contact Information
------------------------------------------------------------------------

   If you have any questions regarding this file contact SPICE support at
   ESAC:

           Marc Costa Sitja
           (+34) 91-8131-457
           mcosta@sciops.esa.int, esa_spice@sciops.esa.int


   or NAIF at JPL:

           Boris Semenov
           +1 (818) 354-8136
           Boris.Semenov@jpl.nasa.gov


End of MK file.
