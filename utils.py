from netCDF4 import Dataset
import pandas as pd
import numpy as np
import os
from scipy import ndimage


def load_data_set():
    cwd = os.getcwd()
    path=os.path.join(os.path.split(cwd)[0],"dataset\\PLP2019\\S2_satellite_images_nc\\")


    #path=os.path.abspath('C:/Users/lavra/Documents/imt_atlantique_2A/projet_s4b2/datas/S2_satellite_images_nc')
    liste_fichier=os.listdir(path)
    data=[]
    for i,fichier in enumerate(liste_fichier):
        to_open=os.path.join(path,fichier)
        data.append(Dataset(to_open))

    config={'lon':'lon','lat':'lat','rhow_442' : 'B01', 'rhow_492' : 'B02', 'rhow_559' : 'B03', 'rhow_665':'B04', 'rhow_704':'B05', 'rhow_739':'B06', 'rhow_780':'B07', 'rhow_833':'B08', 'rhow_864':'B08A', 'rhow_1610':'B11', 'rhow_2186':'B12','rhow_443' : 'B01', 'rhow_492' : 'B02', 'rhow_560' : 'B03', 'rhow_740' : 'B06', 'rhow_783':'B07',  'rhow_865':'B08A', 'rhow_1614':'B11', 'rhow_2202':'B12'}
#sert a prevenir le fait que les satellite n'ont pas exactement la meme valeur de longeur d'onde detecté

    multi_data=pd.DataFrame()


    for i,netcdf_fichier in enumerate(data):
    
        data_frame=pd.DataFrame()
        
        for nom_variable in netcdf_fichier.variables.keys():

            if("rhow" in nom_variable or "lon" in nom_variable or "lat" in nom_variable):
                #d["size"]=numpy_array.shape
                numpy_array=netcdf_fichier["/"+nom_variable][:,:]
                #print(numpy_array)
                shape=numpy_array.shape
                numpy_array=numpy_array.flatten()
                x,y= np.meshgrid(range(shape[1]), range(shape[0]))
                x=x.flatten()
                y=y.flatten()
                data_frame[config[nom_variable]]=numpy_array
                data_frame["x"]=x
                data_frame["y"]=y
                #d[config[nom_variable]]=numpy_array.flatten()
        multi_data=multi_data.append(data_frame.assign(n=netcdf_fichier.isodate[0:10]).set_index('n',append=True).swaplevel(0,1))

    for index in multi_data.index.unique(level=0):#pas d'info sur la photo de 2018

        folder_name=index.replace("-","")
        #path=r"dataset/PLP2019/Vector_Points/"+folder_name+r"/Excel Values/"
        path=os.path.join(os.path.split(cwd)[0],"dataset\\PLP2019\\Vector_Points\\"+folder_name+r"/Excel Values/")
        excel_name=os.listdir(path)[0]
        
        excel=pd.read_excel(path+excel_name)
  
        x_range=netcdf_fichier.xrange
        size_x=int((x_range.max()-x_range.min())/10)
        y_range=netcdf_fichier.yrange
        size_y=int((y_range.max()-y_range.min())/10)

        labels=np.zeros((size_y,size_x))
        for i,j in zip(excel["POINT_X"],excel["POINT_Y"]):
            #les zones des pixels sont approximatifs

            x,y=(i-x_range.min())/10,(j-y_range.min())/10
            if x>=0 and y>=0 and x<size_x and y<size_y:
                x,y=int(x),int(y)
                #print(index+"  ",x,(j-y_range.min())/10)
                labels[size_y-1-y,x]+=1
            
            
            
        #np.save("label-"+str(index),labels)
        #plt.figure()
        #plt.title(index)
        #plt.imshow(labels)
        
        multi_data.loc[index,"label"]=labels.flatten()
    shape=(len(multi_data.y.unique()),len(multi_data.x.unique()))
    for date in multi_data.index.unique(level=0)[0:]:
            
        terre=np.array(multi_data.loc[date]["B01"].isna()).reshape(shape)#quand B01 est NAN, on est sur la terre
        terre=1-terre*1
        terre=ndimage.distance_transform_edt(terre)
        
        multi_data.loc[date,"distance"]=terre.flatten()
    return multi_data