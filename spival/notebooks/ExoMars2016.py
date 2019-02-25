{
    "cells": [
              {
              "cell_type": "markdown",
              "metadata": {},
              "source": [
                         "# ExoMars2016 SPICE Kernel Dataset Status\n",
                         "\n",
                         "Last updated on {current_time} by Marc Costa Sitja (ESAC/ESA). SKD version: {skd_version}\n",
                         "\n",
                         "## Startup\n",
                         "\n",
                         "The metakernel is loaded, the scenario covers a week with a finish time set by the end of coverage of the latest Measured Attitude Kernel."
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "%matplotlib notebook\n",
                         "import spiops\n",
                         "\n",
                         "spiops.load('{metakernel}')   # The meta-kernel is loaded \n",
                         "\n",
                         "start_time = '{start_time_measured}'                                      # Start time\n",
                         "finish_time ='{finish_time_measured}'                                      # Finish time\n",
                         "\n",
                         "interval = spiops.TimeWindow(start_time, finish_time,resolution=60) # spiops object TimeWindow generated\n",
                         "mars = spiops.Target('MARS', time=interval, frame='IAU_MARS')       # spiops object Target Mars generated\n",
                         "tgo = spiops.Observer('TGO', time=interval, target=mars)            # spiops object Observer TGO generated"
                         ]
              },
              {
              "cell_type": "markdown",
              "metadata": {},
              "source": [
                         "## Coverage\n",
                         "\n",
                         "The coverage provided by the SPK and CK files is displayed for the Operational and the Planning meta-kernels."
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "spiops.ck_coverage_timeline('{metakernel}', 'tgo')"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "spiops.spk_coverage_timeline('{metakernel}', 'tgo')"
                         ]
              },
              {
              "cell_type": "markdown",
              "metadata": {},
              "source": [
                         "## Attitude Error\n",
                         "Comparison of +Z axis orientation between predicted and measured attitude in milidegrees."
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "measured_ck = '{skd_path}/ck/{measured_ck}'\n",
                         "predicted_ck = '{skd_path}/ck/{predicted_ck}'\n",
                         "resolution = 16\n",
                         "\n",
                         "spiops.ckdiff_error(measured_ck, predicted_ck, 'TGO_SPACECRAFT', 'J2000', resolution, 0.001, \n",
                         "                    plot_style='circle', utc_start=start_time, utc_finish=finish_time, notebook=True)"
                         ]
              },
              {
              "cell_type": "markdown",
              "metadata": {},
              "source": [
                         "## S/C Structures Orientation\n",
                         "Quaternions, Solar Array Orientation and Solar Aspect Angle, High Gain Antenna Orientation and HGA boresight-Earth Angle."
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('quaternions', notebook=True)         # TGO Orientation (quaternions w.r.. J2000)"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('sa_ang', notebook=True)              # Solar Array (SA) Angles"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('saa_sa', notebook=True)              # SA Solar Aspect Angle"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('hga_angles', notebook=True)          # High Gain Antenna Angles"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('hga_earth', notebook=True)           # High Gain Antenna - Earth Angle"
                         ]
              },
              {
              "cell_type": "markdown",
              "metadata": {},
              "source": [
                         "## Geometry Plots\n",
                         "Series of basic plots for quick geometry assessment. For these plots we set the times to the end of the previous validation report and the generation of the current report."
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "interval.start = '{start_time}'                             \n",
                         "interval.finish = '{finish_time}'"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot3D()                                   # TGO-Mars Orbit in IAU_MARS"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('altitude', notebook=True)            # TGO-Mars Altitude"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('myaxis_target_angle', notebook=True) # TGO -Y Axis and Mars Angle"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('latitude', notebook=True)            # Latitude"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('longitude',notebook=True)            # Longitude"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('groundtrack', notebook=True)         # Groundtrack"
                         ]
              },
              {
              "cell_type": "code",
              "execution_count": null,
              "metadata": {},
              "outputs": [],
              "source": [
                         "tgo.Plot('beta_angle', notebook=True)         # Beta Angle"
                         ]
              }
              ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                    "language": "python",
                        "name": "python3"
                            },
                                "language_info": {
                                    "codemirror_mode": {
"name": "ipython",
    "version": 3
        },
            "file_extension": ".py",
                "mimetype": "text/x-python",
                    "name": "python",
                        "nbconvert_exporter": "python",
                            "pygments_lexer": "ipython3",
                                "version": "3.6.4"
                                }
                                    },
                                        "nbformat": 4,
                                            "nbformat_minor": 2
}
