import adjustText
import urllib.request
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist.floating_axes as floating_axes

from dataclasses import dataclass
from mpl_toolkits.axisartist.grid_finder import (MaxNLocator, DictFormatter)
from matplotlib.transforms import Affine2D
from PIL import Image


class Diamond:
    """Generates a Diamond figure."""

    @dataclass
    class Metric:
        """argument data types expected"""
        data: list
        name: str
        desc: str                        

    def normalize_series(self, serie: pd.Series, factor: float = 0.99) -> pd.Series:
        """Normalize values in a serie."""
        return factor * serie / max(serie)
    
    def quantilize_series(self, serie: pd.Series) -> pd.Series:
        """Define default quantiles in a serie"""
        return serie.quantile([0, 0.5, 0.9]).tolist()
    
    def add_axis(self, figure, position, name, desc):
        """add axis generic function"""
        axis = figure.add_axes(position)                
        axis.text(0.1, 0.95, name, fontsize=10, fontweight='bold', ha='left')
        axis.text(0.1, 0.90, desc, ha='left', va='top',fontsize=8, alpha=0.8, wrap=True)        
        axis.axis(False)
        axis.set_xlim([0, 1])
        axis.set_ylim([0, 1])
        return axis
        
    def add_left_axis(self, figure, metric):
        """addd left axis"""
        position = [0.005, 0.02, 0.3, 0.2]
        return self.add_axis(figure, position, metric.name, metric.desc)  

    def add_right_axis(self, figure, metric):
        """add right axis"""
        position = [0.70, 0.02, 0.3, 0.2]
        return self.add_axis(figure, position, metric.name, metric.desc)    

    def add_title(self, figure, title_text, subtitle_text, logo):
        """add title in the figure"""
        figure.text(0.13, 0.935, title_text, fontweight="bold", fontsize=16)
        figure.text(0.13, 0.905, subtitle_text, fontweight="regular", fontsize=13)

        with urllib.request.urlopen(logo) as url:
            with Image.open(url) as img:                
                img = Image.open(urllib.request.urlopen(logo))
                logo_axis = figure.add_axes([0.015, 0.877, 0.1, 0.1])
                logo_axis.axis(False)
                logo_axis.imshow(img)

        # add footer
        figure.text(1.0, 0.00, "Created using Footbal Viz (https://github.com/fsartoris/football_viz)",ha="right", fontsize=9)

    def rotation(self, transform, max_left, max_right):
        """rotate the figure"""
        left_extent = 1.001
        right_extent = 1.001
        plot_extents = 0, right_extent, 0, left_extent
        
        ticks = list(np.arange(0, 1.1, 0.1))
        left_dict = {tick: '' if tick == 0 else str(round((tick * max_left) / 0.99, 2)) for tick in ticks}
        right_dict = {tick: '' if tick == 0 else str(round((tick * max_right) / 0.99, 2)) for tick in ticks}
            
        tick_formatter1 = DictFormatter(right_dict)
        tick_formatter2 = DictFormatter(left_dict)

        # define axis transformation, build axis and auxillary axis        
        return floating_axes.GridHelperCurveLinear(
            transform,
            plot_extents,
            grid_locator1=MaxNLocator(nbins=1+right_extent/0.1),
            grid_locator2=MaxNLocator(nbins=1+left_extent/0.1),
            tick_formatter1=tick_formatter1,
            tick_formatter2=tick_formatter2
        )   
    
    def create(self, title, subtitle, logo, names, left_metrics, right_metrics):
        """Creates the diamond figure."""

        colors = {"background": '#282828', "font": '#e0e0e0'}
        background_color = colors['background']
        font_color = colors['font']

        # safety cleanup
        left_axis = left_metrics.data.replace(np.nan, 0, inplace=False)
        right_axis = right_metrics.data.replace(np.nan, 0, inplace=False)
        
        # normalize values
        left_normalized = self.normalize_series(serie=left_axis)
        right_normalized = self.normalize_series(serie=right_axis)

        # set quantiles
        left_quantile = self.quantilize_series(serie=left_normalized)
        right_quantile = self.quantilize_series(serie=right_normalized)
        plot_player = names[(left_normalized > left_quantile[2]) | (right_normalized > right_quantile[2])]

        # setup figure
        mpl.rcParams['xtick.color'] = font_color
        mpl.rcParams['ytick.color'] = font_color
        mpl.rcParams['text.color'] = font_color
        figure = plt.figure(figsize=(8.5, 9), facecolor=background_color)

        transform = Affine2D().rotate_deg(45)
        helper = self.rotation(transform, left_axis.max(), right_axis.max())        

        axis = floating_axes.FloatingSubplot(figure, 1, 1, 1, grid_helper=helper)
        axis.patch.set_alpha(0)
        axis.set_position([0.075, 0.07, 0.85, 0.8], which='both')
        aux_axis = axis.get_aux_axes(transform)

        # add transformed axis
        axis = figure.add_axes(axis)
        aux_axis.patch = axis.patch
        axis.axis['left', 'bottom'].line.set_color(font_color)
        axis.axis['right', 'top'].set_visible(False)

        # plot points on auxiliary axis
        aux_axis.scatter(right_normalized,
                         left_normalized,
                         c=left_normalized + right_normalized,
                         cmap='YlGnBu',
                         edgecolor='white',
                         linewidth=0.3, s=50, zorder=2)

        # set axis grid properties
        axis.grid(alpha=0.2, color=font_color, zorder=0)

        # add names in figure
        text = [aux_axis.text(right_normalized[i], left_normalized[i], player, color='white', fontsize=10, zorder=3) for i, player in enumerate(plot_player)]    
        adjustText.adjust_text(text, ax=aux_axis)

        self.add_left_axis(figure, left_metrics)
        self.add_right_axis(figure, right_metrics)        
        self.add_title(figure, title, subtitle, logo)
        
        return plt