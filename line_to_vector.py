# this code runs the process for a single file

fn = '/Users/nastya/Desktop/Diss/Data/tiff/output/output_line30.tif'
nfn = '/Users/nastya/Desktop/Diss/Data/tiff/output/output_line30_thin.tif'

processing.run("grass7:r.thin", {'input':fn,'iterations':200,'output':nfn,'GRASS_REGION_PARAMETER':None,
                                 'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})

processing.run("grass7:r.to.vect", {'input':nfn,'type':0,'column':'value','-s':False,'-v':False,'-z':False,'-b':False,'-t':False,'output':'/Users/nastya/Desktop/myfile.shp',
                                    'GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_OUTPUT_TYPE_PARAMETER':2,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':False})