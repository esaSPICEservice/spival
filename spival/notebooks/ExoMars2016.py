{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# ExoMars2016 SPICE Kernel Dataset Status\n",
    "\n",
    "Last updated on {current_time} by Marc Costa Sitja (ESAC/ESA) \n",
    "SKD version:    {skd_version}\n",
    "SPIVAL version: {spival_version}\n",
    "\n",
    "## Startup and Coverage\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import spiops\n",
    "\n",
    "spiops.load('{metakernel}')                    # The meta-kernel is loaded \n",
    "\n",
    "start_time = '{start_time}'                                # Start time\n",
    "finish_time ='{finish_time}'                                # Finish time\n",
    "\n",
    "interval = spiops.TimeWindow(start_time, finish_time,resolution=60) # spiops object TimeWindow generated\n",
    "mars = spiops.Target('MARS', time=interval, frame='IAU_MARS')       # spiops object Target Mars generated\n",
    "tgo = spiops.Observer('TGO', time=interval, target=mars)            # spiops object Observer TGO generated\n\n",
    "spiops.ck_coverage_timeline('{metakernel}')\n",
    "spiops.spk_coverage_timeline('{metakernel}')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Attitude Error\n",
    "Comparison of -Y axis orientation between predicted and measured attitude in milidegrees "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "resolution = 16\n",
    "\n",
    "measured_ck = '{skd_path}/ck/{measured_ck}'\n",
    "predicted_ck = '{skd_path}/ck/{predicted_ck}'\n",
    "\n",
    "spiops.ckdiff_error(measured_ck, predicted_ck, 'TGO_SPACECRAFT', 'J2000', resolution, 0.0001, \n",
    "                    notebook=True, plot_style='circle', boresight=[0,-1,0])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## S/C Structures Orientation\n",
    "Solar Array Orientation, High Gain Antenna Orientation\n",
    "\n"
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
    "tgo.Plot('hga_earth', notebook=True)           # High Gain Antenna - Earth Angle"
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
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Geometry Plots\n",
    "Basic plots for quick geometry assessment"
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
   "cell_type":       "code",
   "execution_count": null,
   "metadata":        {},
   "outputs":         [],
   "source":          [
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
