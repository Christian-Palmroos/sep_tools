import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


from matplotlib.colors import Normalize
from matplotlib import cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from seppy.loader.solo import mag_load
from seppy.tools import resample_df
from solo_epd_loader import epd_load, calc_ept_corrected_e, combine_channels
from sunpy.coordinates import get_horizons_coord
from sunpy.coordinates import frames
import sunpy.net.attrs as a
import sunpy_soar
from sunpy.net import Fido
from sunpy.timeseries import TimeSeries
from astropy.constants import e, k_B

from multi_inst_plots.other_tools import polarity_rtn, mag_angles, load_goes_xrs, load_solo_stix, plot_goes_xrs, plot_solo_stix, make_fig_axs



# import warnings
# warnings.filterwarnings('ignore')

plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['font.size'] = 12
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rc('axes', titlesize=20)  # fontsize of the axes title
plt.rc('axes', labelsize=20)  # fontsize of the x and y labels
plt.rcParams['agg.path.chunksize'] = 20000



def swa_load_grnd_mom(startdate, enddate, path=None):
    """
    Load SolO/SWA L2 ground moments

    Load-in data for Solar Orbiter/SWA sensor ground moments. Supports level 2
    provided by ESA's Solar Orbiter Archive. Optionally downloads missing
    data directly. Returns data as Pandas dataframe.

    Parameters
    ----------
    startdate, enddate : {datetime, str, or int}
        Datetime object (e.g., dt.date(2021,12,31) or dt.datetime(2021,4,15)),
        "standard" datetime string (e.g., "2021/04/15") or integer of the form
        yyyymmdd with empty positions filled with zeros, e.g. '20210415'
        (enddate must always be later than startdate)
    path : {str}, optional
        Local path for storing downloaded data, by default None

    Returns
    -------
    Pandas dataframe
    """    
    instrument = a.Instrument('SWA')
    time = a.Time(startdate, enddate)
    level = a.Level(2)
    product = a.soar.Product('SWA-PAS-GRND-MOM')
    
    result = Fido.search(instrument & time & level & product)
    files = Fido.fetch(result,path=path)
    
    solo_swa = TimeSeries(files, concatenate=True)
    df_solo_swa = solo_swa.to_dataframe()
    return df_solo_swa

# def rpw_load_radio(startdate, enddate, freq, path=None):
#     """
#     Parameters
#     ----------
#     startdate: dt.datetime 
#     enddate: dt.datetime
#     freq: str
#         TNR or HFR
#     path: str
#     """
#     dl = ParfiveDownloader()
    
#     timerange = TimeRange(startdate, enddate)

#     try:
#         from packaging.version import Version
#         if hasattr(sunpy, "__version__") and Version(sunpy.__version__) >= Version("6.1.0"):
#             pattern = ("https://spdf.gsfc.nasa.gov/pub/data/solar-orbiter/rpw/science/l2/{freq}-surv/{{year:4d}}/solo_l2_rpw-{freq}-surv_{{year:4d}}{{month:2d}}{{day:2d}}_v{version}.cdf")

#             scrap = Scraper(format=pattern, freq=freq.lower(), version="{:2d}") 
#         else:
#             pattern = "https://spdf.gsfc.nasa.gov/pub/data/solar-orbiter/rpw/science/l2/{freq}-surv/%Y/solo_l2_rpw-{freq}-surv_%Y%m%d_v{version}.cdf"
 
#             scrap = Scraper(pattern=pattern, freq=freq.lower(), version="v\\d{2}")  # regex matching "v{any digit}{any digit}""
        
        
#         filelist_urls = scrap.filelist(timerange=timerange)

#         filelist_urls.sort()

#         # After sorting, any multiple versions are next to each other in ascending order.
#         # If there are files with same dates, assume multiple versions -> pop the first one and repeat.
#         # Should end up with a list with highest version numbers. Magic number -7 is the index where 
#         # version number starts

#         i = 0
#         while i < len(filelist_urls) - 1:
#             if filelist_urls[i+1][:-7] == filelist_urls[i][:-7]:
#                 filelist_urls.pop(i)
#             else:
#                 i += 1

#         filelist = [url.split('/')[-1] for url in filelist_urls]

#         if path is None:
#             filelist = [sunpy.config.get('downloads', 'download_dir') + os.sep + file for file in filelist]
#         elif type(path) is str:
#             filelist = [path + os.sep + f for f in filelist]
#         downloaded_files = filelist

#         # Check if file with same name already exists in path
#         for url, f in zip(filelist_urls, filelist):
#             if os.path.exists(f) and os.path.getsize(f) == 0:
#                 os.remove(f)
#             if not os.path.exists(f):
#                 dl.download(url=url, path=f)


#         rpw = TimeSeries(downloaded_files, concatenate=True)
#         df_rpw = rpw.to_dataframe()


#     except (RuntimeError, IndexError):
#         print(f'Unable to obtain SolO RPW-{freq} data for {startdate}-{enddate}!')
#         df_rpw = []
        
#     return df_rpw
    
def read_widget_values(options):
    global plot_electrons
    global plot_protons
    global plot_polarity
    global plot_mag
    global plot_mag_angles
    global plot_radio
    global plot_stix
    global plot_goes
    global plot_Vsw
    global plot_T
    global plot_N
    global stix_ltc
    global viewing
    global startdate
    global enddate
    global plot_ept_e 
    global plot_ept_p 
    global plot_het_e 
    global plot_het_p
    global ept_l3
    global ion_conta_corr
    global path

    path = options.path

    startdate = options.startdt
    enddate = options.enddt

    plot_ept_e = options.solo_ept_e.value
    plot_ept_p = options.solo_ept_p.value
    plot_het_e = options.solo_het_e.value
    plot_het_p = options.solo_het_p.value
    plot_polarity = options.polarity.value
    plot_mag = options.mag.value
    plot_mag_angles = options.mag_angles.value
    plot_radio = options.radio.value
    plot_stix = options.stix.value
    plot_goes = options.goes.value
    plot_Vsw = options.Vsw.value
    plot_T = options.T.value
    plot_N = options.N.value
    stix_ltc = options.stix_ltc.value
    viewing = options.solo_viewing.value

    plot_electrons = plot_ept_e or plot_het_e
    plot_protons = plot_ept_p or plot_het_p

    ept_l3 = True
    ion_conta_corr = False

    if not plot_mag:
        plot_polarity = False

def load_data(options):
    data = {}
    metadata = {}

    global df_ept_org
    global metadata_ept
    global electrons_het
    global electrons_ept
    global protons_ept
    global protons_het
    global df_stix_
    global df_goes_
    global goes_sat
    global swa_data
    global mag_data_org
    global energies_ept
    global energies_het

    read_widget_values(options)

    if plot_electrons or plot_protons:
        
        if ept_l3:
            try:
                df_ept_org, df_rtn_ept, df_hci_ept, energies_ept, metadata_ept = epd_load(sensor='ept', level='l3', pos_timestamp=None,
                                                                                        startdate=startdate, enddate=enddate,
                                                                                        autodownload=True, path=path)
            except UnboundLocalError:
                df_ept_org, df_rtn_ept, df_hci_ept, energies_ept, metadata_ept = [], [], [], [], []
            
            data["ept"] = df_ept_org
            metadata["ept_energies"] = energies_ept
            metadata["ept_other"] = metadata_ept

        else:
            protons_ept, electrons_ept, energies_ept = epd_load(sensor='ept', level='l2', startdate=startdate, enddate=enddate, 
                                                                pos_timestamp=None,viewing=viewing, path=path, autodownload=True)
            # correct EPT level 2 electron data for ion contamination:
            if ion_conta_corr:
                # df_electrons_ept2 = calc_EPT_corrected_e(df_electrons_ept['Electron_Flux'], df_protons_ept['Ion_Flux'])
                electrons_ept = calc_ept_corrected_e(electrons_ept, protons_ept)
                electrons_ept = electrons_ept.mask(electrons_ept < 0)
            
            data["ept_p"] = protons_ept
            data["ept_e"] = electrons_ept
            metadata["ept_energies"] = energies_ept
                
        protons_het, electrons_het, energies_het = epd_load(sensor='het', level='l2', startdate=startdate, enddate=enddate, 
                                                            pos_timestamp=None,viewing=viewing, path=path, autodownload=True)
        
        data["het_e"] = electrons_het
        data["het_p"] = protons_het
        metadata["het_energies"] = energies_het
        

    # if plot_radio:
    #     df_rpw_hfr = rpw_load_radio(startdate=startdate, enddate=enddate, freq="HFR", path=path)
    #     df_rpw_tnr = rpw_load_radio(startdate=startdate, enddate=enddate, freq="TNR", path=path)


    if plot_stix:
        df_stix_ = load_solo_stix(startdate, enddate, resample=None, ltc = stix_ltc)
        data["stix"] = df_stix_


    if plot_goes:
        df_goes_, goes_sat = load_goes_xrs(startdate, enddate, man_select=options.goes_man_select.value, resample=None, path=path)
        data["goes"] = df_goes_


    if plot_mag or plot_mag_angles or plot_polarity:
        try:
            mag_data_org = mag_load(startdate, enddate, level='l2', frame='rtn', path=path)
            mag_data_org['Bmag'] = np.sqrt(np.nansum((mag_data_org.B_RTN_0.values**2, mag_data_org.B_RTN_1.values**2, mag_data_org.B_RTN_2.values**2), axis=0))
        except IndexError:
            print("Unable to obtain MAG data!")
            mag_data_org = []

        data["mag"] = mag_data_org

    if plot_Vsw or plot_N or plot_T:
        try:
            swa_data = swa_load_grnd_mom(startdate, enddate, path=path)
            swa_vsw = np.sqrt(swa_data.V_RTN_0**2 + swa_data.V_RTN_1**2 + swa_data.V_RTN_2**2)
            swa_data['vsw'] = swa_vsw

            temp = np.sqrt(swa_data.TxTyTz_RTN_0**2 + swa_data.TxTyTz_RTN_2**2 + swa_data.TxTyTz_RTN_2**2) * e / k_B 
            swa_data['temp'] = temp
        except IndexError:
            print("Unable to obtain SWA data!")
            swa_data = []

        data["swa"] = swa_data

    return data, metadata


def energy_channel_selection():
    cols = []
    df = pd.DataFrame()

 
    cols.append("EPD/EPT Electrons")
    energy_list_ept_e = pd.Series(energies_ept["Electron_Bins_Text"])
    df = pd.concat([df, energy_list_ept_e], axis=1)


    cols.append("EPD/EPT Protons")
    energy_list_ept_p = pd.Series(energies_ept["Ion_Bins_Text"])
    df = pd.concat([df, energy_list_ept_p], axis=1)


    cols.append("EPD/HET Electrons")
    energy_list_het_e = pd.Series(energies_het["Electron_Bins_Text"])
    df = pd.concat([df, energy_list_het_e], axis=1)


    cols.append("EPD/HET Protons")
    energy_list_het_p = pd.Series(energies_het["H_Bins_Text"])
    df = pd.concat([df, energy_list_het_p], axis=1)

    df.columns = cols
    return df


    

def make_plot(options):
    
    read_widget_values(options)
    
    # Resampling 

    resample_mag = str(options.resample_mag.value) + "min"
    resample = str(options.resample.value) + "min"
    resample_stixgoes = str(options.resample_stixgoes.value) + "min"

    if plot_goes:
        if isinstance(df_goes_, pd.DataFrame) and resample_stixgoes != "0min":
            df_goes = resample_df(df_goes_, resample_stixgoes)
        else:
            df_goes = df_goes_
        
    if plot_stix:
        if isinstance(df_stix_, pd.DataFrame) and resample_stixgoes != "0min":
            df_stix = resample_df(df_stix_, resample_stixgoes)
        else:
            df_stix = df_stix_


    if plot_electrons or plot_protons:
        if plot_electrons:
            if isinstance(electrons_het, pd.DataFrame) and resample != "0min":
                df_electrons_het = resample_df(electrons_het, resample, pos_timestamp=None)
            else:
                df_electrons_het = electrons_het
        if plot_protons:
            if isinstance(protons_het, pd.DataFrame) and resample != "0min":
                df_protons_het = resample_df(protons_het, resample, pos_timestamp=None)
            else:
                df_protons_het = protons_het

        if ept_l3:
            if isinstance(df_ept_org, pd.DataFrame) and resample != "0min":
                df_ept = resample_df(df_ept_org, resample, pos_timestamp=None)
            else:
                df_ept = df_ept_org

            if viewing.lower() == 'south':
                view = 'D'
            else:
                view = viewing[0].upper()

        else:
            if isinstance(electrons_ept, pd.DataFrame) and resample != "0min":
                df_electrons_ept = resample_df(electrons_ept, resample, pos_timestamp=None)
            else:
                df_electrons_ept = electrons_ept
            if isinstance(protons_ept, pd.DataFrame) and resample != "0min":
                df_protons_ept = resample_df(protons_ept, resample, pos_timestamp=None)
            else:
                df_protons_ept = protons_ept


    if plot_Vsw or plot_N or plot_T:
        if isinstance(swa_data, pd.DataFrame):
            if resample_mag == "0min":
                df_swa = resample_df(swa_data, "5s", pos_timestamp=None)    
            else:
                df_swa = resample_df(swa_data, resample_mag, pos_timestamp=None)
        else:
            df_swa = swa_data

    if plot_mag or plot_mag_angles or plot_polarity:
        if isinstance(mag_data_org, pd.DataFrame):
            if resample_mag == "0min":
                # dataframe is very high cadence and so here we apply a minimum of 5 s to lighten the load
                mag_data = resample_df(mag_data_org, "5s", pos_timestamp=None)
            else:
                mag_data = resample_df(mag_data_org, resample_mag, pos_timestamp=None)
        else:
            mag_data = mag_data_org


    ept_ele_channels = options.solo_ch_ept_e.value
    het_ele_channels = options.solo_ch_het_e.value
    ept_p_channels = options.solo_ch_ept_p.value
    het_p_channels = options.solo_ch_het_p.value
    av_en = False

    legends_inside = options.legends_inside.value
    cmap = options.radio_cmap.value

    
    if plot_electrons or plot_protons:
        print("Chosen energy channels:")
        if plot_ept_e:
            print(f"EPT electrons: {ept_ele_channels}, {len(ept_ele_channels)}")
        if plot_het_e:
            print(f"HET electrons: {het_ele_channels}, {len(het_ele_channels)}")
            
        if plot_ept_p:
            print(f"EPT protons: {ept_p_channels}, {len(ept_p_channels)}")
        if plot_het_p:
            print(f"HET protons: {het_p_channels}, {len(het_p_channels)}")
        

    fig, axs = make_fig_axs(options)

    font_ylabel = 20
    font_legend = 10
    color_offset = 3

    i = 0

    # # ### Radio

    # if plot_radio:
    #     vmin, vmax = 500, 1e7
    #     log_norm = LogNorm(vmin=vmin, vmax=vmax)

    #     if isinstance(df_rpw_hfr, pd.DataFrame):
    #         TimeHFR2D, FreqHFR2D = np.meshgrid(df_rpw_hfr.index, df_rpw_hfr.columns, indexing='ij')
    #         TimeTNR2D, FreqTNR2D = np.meshgrid(df_rpw_tnr.index, df_rpw_tnr.columns, indexing='ij')

    #         # Create colormeshes. Shading option flat and thus the removal of last row and column are there to solve the time jump bar problem, 
    #         # when resampling isn't used
    #         mesh = axs[i].pcolormesh(TimeTNR2D, FreqTNR2D, df_rpw_tnr.iloc[:-1,:-1], shading='flat', cmap='jet', norm=log_norm)
    #         axs[i].pcolormesh(TimeHFR2D, FreqHFR2D, df_rpw_hfr.iloc[:-1,:-1], shading='flat', cmap='jet', norm=log_norm) 

    #         # Add inset axes for colorbar
    #         axins = inset_axes(axs[i], width="100%", height="100%", loc="center", bbox_to_anchor=(1.05,0,0.03,1), bbox_transform=axs[i].transAxes, borderpad=0.2)
    #         cbar = fig.colorbar(mesh, cax=axins, orientation="vertical")
    #         cbar.set_label("Intensity (sfu)", rotation=90, labelpad=10, fontsize=font_ylabel)

    #     axs[i].set_yscale('log')
    #     axs[i].set_ylabel("Frequency (MHz)", fontsize=font_ylabel)
        
        
    #     i += 1

    ### STIX
    if plot_stix:
        plot_solo_stix(df_stix, axs[i], stix_ltc, legends_inside, font_ylabel)
        i += 1 

    if plot_goes:
        plot_goes_xrs(options=options, data=df_goes, sat=goes_sat, ax=axs[i], font_legend=font_legend)
        i += 1

    ### Electrons
    ch_key = 'Electron_Bins_Text'
    e_key = 'Electron_Flux'
    p_key = 'Ion_Flux'
    p_ch_key = "Ion_Bins_Text"
    #e_channels = np.arange(0, 15, 3) #[2, 10, 19, 25]
    if plot_electrons:        
        if av_en and plot_ept_e:
            try:
                ch_start = 0
                ch_end = len(energies_ept[ch_key])
                ch_step = 4
                num_channels = np.intc((ch_end-ch_start)/ch_step)
                axs[i].set_prop_cycle('color', plt.cm.Blues_r(np.linspace(0,1,num_channels+color_offset)))

                for k in np.arange(ch_start, ch_end-ch_step, ch_step):
                    channel = [k, k+ch_step-1]
                    #av_flux, en_channel_string = calc_av_en_flux_EPD(df_electrons_ept, energies_ept, channel, 'e', 'ept')
                    av_flux, en_channel_string = combine_channels(df_electrons_ept, energies_ept, channel, 'ept', viewing=viewing, species='e')
                    axs[i].plot(av_flux, ds="steps-mid", label='EPT '+en_channel_string)    
            except TypeError:
                pass

        else:
            if plot_ept_e:
                if ept_l3:
                    axs[i].set_prop_cycle('color', plt.cm.Greens_r(np.linspace(0,1,len(ept_ele_channels)+color_offset)))
                    # for k, e in enumerate(energies_ept['Electron_Bins_Text']):
                    try:
                        for chan in ept_ele_channels:
                            axs[i].plot(df_ept[f'Electron_Corrected_Flux_{view}_{chan}'], ds="steps-mid", label=f"EPT {energies_ept['Electron_Bins_Text'][chan]}")
                    except TypeError:
                        pass
                else:
                    ch_start = 0
                    ch_end = len(energies_ept[ch_key])
                    ch_step = 1
                    for k in np.arange(ch_start, ch_end-ch_step, ch_step):
                        if ion_conta_corr:
                            axs[i].plot(df_electrons_ept[f'{e_key}_{k}'],
                                        ds="steps-mid", label='EPT '+energies_ept[ch_key][k][0]) 
                        else:
                            axs[i].plot(df_electrons_ept['Electron_Flux'][f'{e_key}_{k}'],
                                        ds="steps-mid", label='EPT '+energies_ept[ch_key][k][0])                  

        if plot_het_e:
            axs[i].set_prop_cycle('color', plt.cm.Blues_r(np.linspace(0.,1,len(het_ele_channels)+color_offset)))
            try:
                for channel in het_ele_channels:
                    axs[i].plot(df_electrons_het['Electron_Flux'][f'{e_key}_{channel}'],
                                ds="steps-mid", label='HET '+energies_het[ch_key].flatten()[channel])
            except TypeError:
                pass

        axs[i].set_yscale('log')
        axs[i].set_ylabel("Intensity\n"+r"[(cm$^2$ sr s MeV)$^{-1}]$", fontsize=font_ylabel)
        
        title = f'Electrons ({viewing})'
        if legends_inside:
            axs[i].legend(loc='upper right', borderaxespad=0., fontsize=font_legend, title=title)
        else:
            axs[i].legend(loc='upper left', borderaxespad=0., fontsize=font_legend, bbox_to_anchor=(1.01, 1), title=title)
        i += 1



    ### Protons
    if plot_protons:
        if av_en and plot_ept_p:
            ch_start = 0
            ch_end = 64
            ch_step = 7
            num_channels = np.intc((ch_end-ch_start)/ch_step)
            axs[i].set_prop_cycle('color', plt.cm.Wistia_r(np.linspace(0,1,num_channels+color_offset)))

            for k in np.arange(ch_start, ch_end-ch_step, ch_step):
                channel = [k, k+ch_step-1]
                #av_flux, en_channel_string = calc_av_en_flux_EPD(df_protons_ept, energies_ept, channel, 'p', 'ept')
                av_flux, en_channel_string = combine_channels(df_protons_ept, energies_ept, channel, 'ept', viewing=None, species='p')
                axs[i].plot(av_flux, ds="steps-mid", label='EPT '+en_channel_string)    

            ch_start = 0
            ch_end = len(energies_het['H_Bins_Text'])-1
            ch_step = 5
            num_channels = np.intc((ch_end-ch_start)/ch_step)                
            axs[i].set_prop_cycle('color', plt.cm.Reds_r(np.linspace(0.3,1,num_channels)))
            for k in np.arange(ch_start, ch_end-ch_step, ch_step):
                channel = [k, k+ch_step-1]
                #av_flux, en_channel_string = calc_av_en_flux_EPD(df_protons_het, energies_het, channel, 'p', 'het')
                av_flux, en_channel_string = combine_channels(df_protons_het, energies_het, channel, 'het', viewing=None, species='p')
                axs[i].plot(av_flux, ds="steps-mid", label='HET '+en_channel_string)
            

        else:
            try:
                if plot_ept_e:
                    if ept_l3:
                        axs[i].set_prop_cycle('color', plt.cm.Wistia_r(np.linspace(0,1,len(ept_p_channels)+color_offset)))
                        # for k, e in enumerate(energies_ept['Ion_Bins_Text']):
                        for chan in ept_p_channels:                    
                            axs[i].plot(df_ept[f'Ion_Flux_{view}_{chan}'], ds="steps-mid", label=f"EPT {energies_ept['Ion_Bins_Text'][chan]}")
                    else:
                        p_channels = np.arange(0, 64, 6)
                        axs[i].set_prop_cycle('color', plt.cm.Wistia_r(np.linspace(0.2,1,len(p_channels))))
                        for channel in p_channels:
                            axs[i].plot(df_protons_ept['Ion_Flux'][f'{p_key}_{channel}'],
                                        ds="steps-mid", label='EPT '+energies_ept[p_ch_key][channel][0])    
                            
                if plot_het_p:    
                    axs[i].set_prop_cycle('color', plt.cm.Reds_r(np.linspace(0,1,len(het_p_channels)+color_offset)))
                    for channel in het_p_channels:
                        axs[i].plot(df_protons_het['H_Flux'][f'H_Flux_{channel}'],
                                    ds="steps-mid", label='HET '+energies_het["H_Bins_Text"].flatten()[channel])
                        
            except TypeError:
                pass
        axs[i].set_yscale('log')
        axs[i].set_ylabel("Intensity\n"+r"[(cm$^2$ sr s MeV)$^{-1}$]", fontsize=font_ylabel)
        title = f'Protons/Ions ({viewing})'
        if legends_inside:
            axs[i].legend(loc='upper right', borderaxespad=0., fontsize=font_legend, title=title)
        else:
            axs[i].legend(loc='upper left', borderaxespad=0., fontsize=font_legend, bbox_to_anchor=(1.01, 1), title=title)
        
        i += 1    

        
    ### Mag
    if plot_mag:
        ax = axs[i]
        # Bmag = np.sqrt(np.nansum((df_mag.B_r.values**2,mag_data.B_t.values**2,mag_data.B_n.values**2), axis=0))
        if isinstance(mag_data, pd.DataFrame):
            ax.plot(mag_data.index, mag_data.Bmag, label='B', color='k', linewidth=1)
            ax.plot(mag_data.index.values, mag_data.B_RTN_0.values, label='Br', color='dodgerblue')
            ax.plot(mag_data.index.values, mag_data.B_RTN_1.values, label='Bt', color='limegreen')
            ax.plot(mag_data.index.values, mag_data.B_RTN_2.values, label='Bn', color='deeppink')
        ax.axhline(y=0, color='gray', linewidth=0.8, linestyle='--')
        # ax.legend(loc='upper right')#, bbox_to_anchor=(1, 0.5))
        if legends_inside:
            axs[i].legend(loc='upper right', borderaxespad=0., 
                          fontsize=font_legend)
        else:
            axs[i].legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0., 
                          fontsize=font_legend)

        ax.set_ylabel('B [nT]', fontsize=font_ylabel)
        ax.tick_params(axis="x",direction="in", which='both')#, pad=-15)
        i += 1

        if plot_polarity and isinstance(mag_data, pd.DataFrame):
            pos = get_horizons_coord('Solar Orbiter', time={'start':mag_data.index[0]-pd.Timedelta(minutes=15), 'stop':mag_data.index[-1]+pd.Timedelta(minutes=15), 'step':"1min"})  # (lon, lat, radius) in (deg, deg, AU)
            pos = pos.transform_to(frames.HeliographicStonyhurst())
            #Interpolate position data to magnetic field data cadence
            r = np.interp([t.timestamp() for t in mag_data.index], [t.timestamp() for t in pd.to_datetime(pos.obstime.value)], pos.radius.value)
            lat = np.interp([t.timestamp() for t in mag_data.index], [t.timestamp() for t in pd.to_datetime(pos.obstime.value)], pos.lat.value)
            pol, phi_relative = polarity_rtn(mag_data.B_RTN_0.values, mag_data.B_RTN_1.values, mag_data.B_RTN_2.values, r, lat, V=400)
            # create an inset axe in the current axe:
            pol_ax = inset_axes(ax, height="5%", width="100%", loc=9, bbox_to_anchor=(0.,0,1,1.1), bbox_transform=ax.transAxes) # center, you can check the different codes in plt.legend?
            pol_ax.get_xaxis().set_visible(False)
            pol_ax.get_yaxis().set_visible(False)
            pol_ax.set_ylim(0,1)
            pol_ax.set_xlim([mag_data.index.values[0], mag_data.index.values[-1]])
            pol_arr = np.zeros(len(pol))+1
            timestamp = mag_data.index.values[2] - mag_data.index.values[1]
            norm = Normalize(vmin=0, vmax=180, clip=True)
            mapper = cm.ScalarMappable(norm=norm, cmap=cm.bwr)
            pol_ax.bar(mag_data.index.values[(phi_relative>=0) & (phi_relative<180)], pol_arr[(phi_relative>=0) & (phi_relative<180)], color=mapper.to_rgba(phi_relative[(phi_relative>=0) & (phi_relative<180)]), width=timestamp)
            pol_ax.bar(mag_data.index.values[(phi_relative>=180) & (phi_relative<360)], pol_arr[(phi_relative>=180) & (phi_relative<360)], color=mapper.to_rgba(np.abs(360-phi_relative[(phi_relative>=180) & (phi_relative<360)])), width=timestamp)
            pol_ax.set_xlim(options.plot_start, options.plot_end)

        
    if plot_mag_angles:
        ax = axs[i]
        # Bmag = np.sqrt(np.nansum((mag_data.B_RTN_0.values**2,mag_data.B_RTN_1.values**2,mag_data.B_RTN_2.values**2), axis=0))    
        
        if isinstance(mag_data, pd.DataFrame):
            alpha, phi = mag_angles(mag_data['Bmag'], mag_data.B_RTN_0.values, mag_data.B_RTN_1.values, mag_data.B_RTN_2.values)
            ax.plot(mag_data.index, alpha, '.k', label='alpha', ms=1)
        ax.axhline(y=0, color='gray', linewidth=0.8, linestyle='--')
        ax.set_ylim(-90, 90)
        ax.set_ylabel(r"$\Theta_\mathrm{B}$ [°]", fontsize=font_ylabel)
        # ax.set_xlim(X1, X2)
        ax.tick_params(axis="x",direction="in", pad=-15)

        i += 1
        ax = axs[i]
        if isinstance(mag_data, pd.DataFrame):
            ax.plot(mag_data.index, phi, '.k', label='phi', ms=1)
        ax.axhline(y=0, color='gray', linewidth=0.8, linestyle='--')
        ax.set_ylim(-180, 180)
        ax.set_ylabel(r"$\Phi_\mathrm{B}$ [°]", fontsize=font_ylabel)
        # ax.set_xlim(X1, X2)
        ax.tick_params(axis="x",direction="in", which='both', pad=-15)
        i += 1
    
    ### Temperature
    if plot_T:
        if isinstance(df_swa, pd.DataFrame):
            axs[i].plot(df_swa.index, df_swa['T'], '-k', label="Temperature")
        axs[i].set_ylabel(r"T$_\mathrm{p}$ [K]", fontsize=font_ylabel)
        axs[i].set_yscale('log')
        i += 1

    ### Density
    if plot_N:
        if isinstance(df_swa, pd.DataFrame):
            axs[i].plot(df_swa.index, df_swa.N,
                        '-k', label="Ion density")
        axs[i].set_ylabel(r"N$_\mathrm{p}$ [cm$^{-3}$]", fontsize=font_ylabel)
        
        i += 1

    ### Sws
    if plot_Vsw:
        if isinstance(df_swa, pd.DataFrame):
            axs[i].plot(df_swa.index, df_swa.vsw,
                        '-k', label="Bulk speed")
        axs[i].set_ylabel(r"V$_\mathrm{sw}$ [km s$^{-1}$]", fontsize=font_ylabel)
        i += 1
    
    plt.show()

    return fig, axs



