program read_radar
implicit none

integer ixyz, jxyz, kxyz, i, j, k, irec
parameter (ixyz=201, jxyz=201, kxyz=40)
real      dbz(ixyz, jxyz, kxyz)

open (unit=21, &
     &      file='/home/eejmh/Desktop/read_radar_mirai/mirai151123_011200.cappi.dbz', &
     &      form='unformatted', &
     &      access='direct',recl=ixyz*4)
open (unit=22, file='/home/eejmh/Desktop/read_radar_mirai/mirai151123_011200.cappi.dbz.txt')
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

