import numpy as np


# ========================================================= #
# ===  vtk_makeImageData class                          === #
# ========================================================= #
class vtk_makeImageData():
    # ------------------------------------------------- #
    # --- class Initiator                           --- #
    # ------------------------------------------------- #
    def __init__( self, vtkFile=None, Data=None, \
                  Spacing=[1.,1.,1.], Origin=[0.,0.,0.,]):
        # --- [1-1] Arguments                       --- #
        if ( vtkFile is None ): vtkFile = "out.vti"
        # --- [1-2] Variables Settings              --- #
        self.vtkFile     = vtkFile
        self.vtkContents = ''
        self.vtkEndTags  = ''
        self.Data        = Data
        self.DataType    = None
        self.DataDim     = None
        self.LILJLK      = None
        self.nDataCounts = 1
        self.Origin      = Origin
        self.Spacing     = Spacing
        self.DataFormat  = "ascii"
        self.vtk_inquireDataType()
        print( self.Data.dtype, self.DataType )
        # --- [1-3] Routines                        --- #
        self.vtk_add_VTKFileTag  ( datatype="ImageData" )
        self.vtk_add_ImageDataTag()
        self.vtk_add_PointDataTag()
        self.vtk_writeFile()

    # ------------------------------------------------- #
    # --- vtk_add_VTKFileTag                        --- #
    # ------------------------------------------------- #
    def vtk_add_VTKFileTag( self, datatype=None ):
        if ( datatype is None ): datatype = "ImageData"
        self.vtkContents  = self.vtkContents + '<?xml version="1.0"?>\n'
        self.vtkContents  = self.vtkContents + '<VTKFile type="{0}">\n'.format( datatype )
        self.vtkEndTags   = '</VTKFile>'     + '\n' + self.vtkEndTags
        
    # ------------------------------------------------- #
    # --- vtk_add_ImageDataTag                      --- #
    # ------------------------------------------------- #
    def vtk_add_ImageDataTag( self, LILJLK=None, Origin=None, Spacing=None ):
        if ( LILJLK    is not None ): self.LILJLK    = LILJLK
        if ( Spacing   is not None ): self.Spacing   = Spacing
        if ( Origin    is not None ): self.Origin    = Origin
        self.vtkContents  = self.vtkContents + '<ImageData WholeExtent="{0}" Origin="{1}" Spacing="{2}">\n'
        self.WholeExtent  = " ".join( [ "0 {0}".format( max(s-1,0) ) for s in list( self.LILJLK ) ] )
        self.Origin       = " ".join( [ str(Opt) for Opt in self.Origin    ] )
        self.Spacing      = " ".join( [ str(Spc) for Spc in self.Spacing   ] )
        self.vtkContents  = self.vtkContents.format( self.WholeExtent, self.Origin, self.Spacing )
        self.vtkEndTags   = '</ImageData>\n' + self.vtkEndTags

    # ------------------------------------------------- #
    # --- vtk_add_PointDataTag                      --- #
    # ------------------------------------------------- #
    def vtk_add_PointDataTag( self, extent=None, DataType=None, DataName=None ):
        if ( extent    is     None ): extent     = self.WholeExtent
        if ( DataType  is     None ): DataType   = "Scalars"
        if ( DataName  is     None ):
            self.DataName    = "Data{0}".format( self.nDataCounts )
            self.nDataCounts = self.nDataCounts + 1
        self.vtkContents  = self.vtkContents + '<Piece Extent="{0}">\n'.format( extent )
        self.vtkContents  = self.vtkContents + '<PointData {0}="{1}">\n'.format( DataType, self.DataName )
        self.vtk_add_DataArray( DataName=DataName )
        self.vtkEndTags   = '</Piece>\n'     + self.vtkEndTags
        self.vtkEndTags   = '</PointData>\n' + self.vtkEndTags
        self.vtkContents  = self.vtkContents.format( extent )

    # ------------------------------------------------- #
    # --- vtk_add_DataArray                         --- #
    # ------------------------------------------------- #
    def vtk_add_DataArray( self, Data=None, DataName=None, DataFormat=None, DataType=None, NumberOfComponents=1 ):
        if ( Data       is     None ): Data       = self.Data
        if ( DataName   is     None ): DataName   = self.DataName
        if ( DataFormat is     None ): DataFormat = self.DataFormat
        if ( DataType   is     None ): DataType   = self.DataType
        self.vtkContents = self.vtkContents + '<DataArray type="{0}" NumberOfComponents="{1}" Name="{2}" format="{3}">\n'
        lines = ""
        if ( NumberOfComponents == 1 ):
            for line in np.ravel( Data ):
                lines += "{0} ".format( line )
        else:
            for line in Data:
                lines += " ".join( [ str( val ) for val in line ] ) + "\n"
        self.vtkContents = self.vtkContents + lines
        self.vtkContents = self.vtkContents.format( DataType, NumberOfComponents, DataName, DataFormat )
        self.vtkContents = self.vtkContents + '</DataArray>\n'

    
    # ------------------------------------------------- #
    # --- vtk_writeFile                             --- #
    # ------------------------------------------------- #
    def vtk_writeFile( self, vtkFile=None ):
        if ( vtkFile is not None ): self.vtkFile = "out.vti"
        with open( self.vtkFile, "w" ) as f:
            f.write( self.vtkContents )
            f.write( self.vtkEndTags  )


    # ------------------------------------------------- #
    # --- vtk_JudgeDataType                         --- #
    # ------------------------------------------------- #
    def vtk_inquireDataType( self, Data=None ):
        if ( Data is None ): Data = self.Data
        if ( Data is None ): return( None )
        if ( type( Data ) is not np.ndarray ):
            print( "[vtk_JudgeDataType] Data should be np.ndarray [ERROR]" )
        else:
            if ( Data.dtype == np.int64   ): self.DataType = "Int64"
            if ( Data.dtype == np.float64 ): self.DataType = "Float64"
            self.DataDims  = ( self.Data ).ndim
            self.DataShape = ( self.Data ).shape
            if ( self.DataDims == 2 ):
                self.LILJLK = np.concatenate( ( self.DataShape, np.zeros((1,),dtype=np.int64) ) )
            print( self.LILJLK )

            
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    import myUtils.genArgs as gar
    args    = gar.genArgs()
    # Data    = ( np.arange( 100 ) ).reshape( (20,5) )
    # Data    = ( np.linspace( 0.,10.,121 ) ).reshape( 11, 11 )
    import genGrid.Gaussian2D as gs2
    gau     = gs2.Gaussian2D( x1Range=[-1.0,1.0], x2Range=[-1.0,1.0], size=(101,101) )
    vtk     = vtk_makeImageData( Data=gau )
