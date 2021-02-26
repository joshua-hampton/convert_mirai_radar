#!/bin/bash
#lon0=$1
#lat0=$2
#inputfile=$3
#outputfile=$4
inputfile=$1
infofile=$2
outputfile=$3

if [ -z ${outputfile} ]
then
  outputfile=None
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cat << End_Of_Fortran_Code | sed -e 's/#.*//; s/  *$//' > ${DIR}/read_radar.f90
program read_radar
implicit none

integer ixyz, jxyz, kxyz, i, j, k, irec
parameter (ixyz=201, jxyz=201, kxyz=40)
real      dbz(ixyz, jxyz, kxyz)

open (unit=21, &
     &      file='${inputfile}', &
     &      form='unformatted', &
     &      access='direct',recl=ixyz*4)
open (unit=22, file='${inputfile}.txt')
irec=0
   do k=1,kxyz
      do j=1,jxyz
         irec=1+irec
         read (21,rec=irec) (dbz(i,j,k),i=1,ixyz)
         write(22,*) (dbz(i,j,k),i=1,ixyz)
      enddo
   enddo
close(21)
close(22)

end program read_radar

End_Of_Fortran_Code

gfortran ${DIR}/read_radar.f90 -o ${DIR}/read_radar.exe
${DIR}/read_radar.exe

#python ${DIR}/text_to_netcdf.py ${inputfile}.txt -l ${lon0} -a ${lat0}
python ${DIR}/text_to_netcdf.py ${inputfile}.txt -f ${infofile} -o ${outputfile}

# clean up
rm ${inputfile}.txt