import sys
import numpy as np


# ========================================================= #
# ===  vtk_makeLineData class                           === #
# ========================================================= #
class vtk_makeLineData():
    # ------------------------------------------------- #
    # --- class Initiator                           --- #
    # ------------------------------------------------- #
    def __init__( self, vtkFile=None, xyz=None, Data=None, DataName=None ):
        # --- [1-1] Arguments                       --- #
        if ( vtkFile is None ): vtkFile = "out.vtp"
        # --- [1-2] Variables Settings              --- #
        self.vtkFile      = vtkFile
        self.vtkContents  = ''
        self.vtkEndTags   = ''
        self.xyz          = xyz
        self.xyzDim       = None
        self.Data         = Data
        self.DataType     = None
        self.DataLen      = None
        self.DataName     = DataName
        self.NoLines      = 1
        self.NoComponents = 3
        self.nDataCounts  = 1
        self.DataFormat   = "ascii"
        if ( self.xyz      is None ): sys.exit( "[makeLineData]  xyz is not defined... [ERROR]" )
        if ( self.DataName is None ): self.DataName = "Line1"
        # --- [1-3] Routines                        --- #
        self.vtk_inquireDataType()
        self.vtk_add_VTKFileTag  ( datatype="PolyData" )
        self.vtk_add_PolyDataTag()
        self.vtk_writeFile()

    # ------------------------------------------------- #
    # --- vtk_add_VTKFileTag                        --- #
    # ------------------------------------------------- #
    def vtk_add_VTKFileTag( self, datatype=None ):
        if ( datatype is None ): datatype = "PolyData"
        self.vtkContents  = self.vtkContents + '<?xml version="1.0"?>\n'
        self.vtkContents  = self.vtkContents + '<VTKFile type="{0}">\n'.format( datatype )
        self.vtkEndTags   = '</VTKFile>\n'   + self.vtkEndTags

    # ------------------------------------------------- #
    # --- vtk_add_PolyDataTag                       --- #
    # ------------------------------------------------- #
    def vtk_add_PolyDataTag( self, xyz=None, Data=None, NoPoints=None, NoLines=None, NoVerts=None, NoStrips=None, NoPolys=None ):
        if ( xyz      is None ): xyz      = self.xyz
        if ( Data     is None ): Data     = self.Data
        if ( NoPoints is None ): NoPoints = self.DataLen
        if ( NoLines  is None ): NoLines  = self.DataLen - 1
        if ( NoVerts  is None ): NoVerts  = 0
        if ( NoStrips is None ): NoStrips = 0
        if ( NoPolys  is None ): NoPolys  = 0
        self.vtkContents  = self.vtkContents + '<PolyData>\n'
        self.vtkEndTags   = '</PolyData>\n'  + self.vtkEndTags
        self.vtkContents  = self.vtkContents + \
                            '<Piece NumberOfPoints="{0}" NumberOfLines="{1}" '\
                            'NumberOfVerts="{2}" NumberOfStrips="{3}" NumberOfPolys="{4}">\n'\
                            .format( NoPoints, NoLines, NoVerts, NoStrips, NoPolys )
        self.vtkContents  = self.vtkContents + self.vtk_add_PointsAndLines( xyz=xyz, Data=Data )
        self.vtkEndTags   = '</Piece>\n' + self.vtkEndTags

    # ------------------------------------------------- #
    # --- vtk_add_points                            --- #
    # ------------------------------------------------- #
    def vtk_add_PointsAndLines( self, xyz=None, Data=None, DataType=None, DataName=None, \
                                DataFormat=None, NoComponents=None ):
        if ( xyz          is     None ): xyz          = self.xyz
        if ( Data         is     None ): Data         = self.Data
        if ( DataName     is     None ): DataName     = self.DataName
        if ( DataFormat   is     None ): DataFormat   = self.DataFormat
        if ( NoComponents is     None ): NoComponents = self.NoComponents
        if ( DataType     is     None ): DataType     = self.DataType
        Block1       = ""
        Block2       = ""
        Block3       = ""
        Block1      += '<PointData Scalars="{0}">\n'.format( DataName )
        Block1      += '<DataArray type="{0}" Name="{1}" format="{2}">\n'\
                                         .format( DataType, DataName, DataFormat )
        for hData in Data:
            Block1  += "{0} ".format( hData )
        Block1      += '</DataArray>'
        Block1      += '</PointData>\n'
        Block2      += '<Points>\n'
        Block2      += '<DataArray NumberOfComponents="{0}" type="{1}" Name="points" format="{2}">\n'\
                                                .format( NoComponents, DataType, DataFormat )
        for hxyz in xyz:
            Block2  += "{0} {1} {2}\n".format( hxyz[0], hxyz[1], hxyz[2] )
        Block2      += "</DataArray>\n"
        Block2      += '</Points>\n'
        Block3       = '<Lines>\n'
        Block3      += '<DataArray type="Int32" format="{0}" Name="connectivity">\n'.format( DataFormat )
        for ik in range( self.DataLen-1 ):
            Block3  += "{0} {1}\n".format( ik, ik+1 )
        Block3      += "</DataArray>\n"
        Block3      += '<DataArray type="Int32" format="{0}" Name="offsets">\n'.format( DataFormat )
        for ik in range( self.DataLen-1 ):
            Block3  += "{0} ".format( int(2*(ik+1)) )
        Block3      += "\n"
        Block3      += "</DataArray>\n"
        Block3      += '</Lines>\n'
        return( Block1 + Block2 + Block3 )
    
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
            self.xyzDims  = ( self.xyz ).ndim
            if   ( self.xyzDims == 2 ):
                self.DataLen      = self.xyz.shape[0]
                self.NoComponents = self.xyz.shape[1]
            elif ( self.xyzDims == 3 ):
                self.DataLen      = self.xyz.shape[0]
                self.NoComponents = self.xyz.shape[1]
                self.NoLines      = self.xyz.shape[2]
            else:
                print( "[vtk_inquiryDataType] Data Dimension == {0} ???".format( self.xyzDims ) )
            print( "[vtk_inquiryDataType] xyz shape :: ", self.xyz.shape )
            
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    import myUtils.genArgs as gar
    args    = gar.genArgs()
    tAxis   = np.linspace( 0.0, 100.0, 10001 )
    xAxis   = np.cos( 2.*np.pi*tAxis        )
    yAxis   = np.sin( 2.*np.pi*tAxis        )
    zAxis   = np.sin( 2.*np.pi*tAxis * 0.01 )
    import myConvert.pilearr  as pil
    xyz     = np.transpose( pil.pilearr( (xAxis,yAxis,zAxis), axis=1 ) )
    Data    = np.copy( tAxis )
    vtk     = vtk_makeLineData( xyz=xyz, Data=Data )
