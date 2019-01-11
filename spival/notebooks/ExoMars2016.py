{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# ExoMars2016 SPICE Kernel Dataset Status\n",
    "\n",
    "Last updated on {current_time} by Marc Costa Sitja (ESAC/ESA)SKD version: {skd_version}\n",
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
    "spiops.load('{metakernel}')\n",
    "\n",
    "start_time = '{start_time}'\n",
    "finish_time ='{finish_time}'\n",
    "\n",
    "interval = spiops.TimeWindow(start_time, finish_time,resolution=60)\n",
    "\n",
    "mars = spiops.Target('MARS', time=interval, frame='IAU_MARS')\n",
    "tgo = spiops.Observer('TGO', time=interval, target=mars)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Geometry Plots"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "tgo.Plot('distance', notebook=True)\n",
    "tgo.Plot('zaxis_target_angle', notebook=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "resolution = 4\n",
    "tolerance = 0.0001  #[DEG]\n",
    "spacecraft_frame = 'TGO_SPACECRAFT'\n",
    "target_frame = 'J2000'"
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
    "\n",
    "spiops.ckdiff_error(measured_ck, predicted_ck, spacecraft_frame, target_frame,\n",
    "                    resolution, tolerance, notebook=True,\n",
    "                    plot_style='circle')"
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
