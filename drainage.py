import shapefile
import math
import numpy
from PIL import Image
def inPolygon(x, y, xp, yp, hs, hflag):
	flag=False
	if hflag:
		for i in range(len(xp)-1):
			if not((i+1) in hs):
				if (((yp[i+1]<=y and y<yp[i]) or (yp[i]<=y and y<yp[i+1])) and (x>(xp[i]-xp[i+1])*(y-yp[i+1])/(yp[i]-yp[i+1])+xp[i+1])):
					flag=not(flag)
	else:
		for i in range(len(xp)):
			if (((yp[i]<=y and y<yp[i-1]) or (yp[i-1]<=y and y<yp[i])) and (x>(xp[i-1]-xp[i])*(y-yp[i])/(yp[i-1]-yp[i])+xp[i])):
				flag=not(flag)
	return flag
def triangle_altitude(xa, ya, xb, yb, xc, yc):
	cx=xb-xa
	cy=yb-ya
	a=math.sqrt((xb-xc)**2+(yb-yc)**2)
	b=math.sqrt((xa-xc)**2+(ya-yc)**2)
	c=math.sqrt((xb-xa)**2+(yb-ya)**2)
	cosa=(b*b+c*c-a*a)/(2*b*c)
	if cosa>=1:
		return 0, True
	else:
		sina=math.sqrt(1-cosa*cosa)
		h=sina*b
		hx=abs(h*cy/c)
		hy=abs(h*cx/c)
		cc=0
		if (cx>=0 and cy>=0):
			xh=xc-hx
			yh=yc+hy
			cc+=1
			if ((xh>=xa and xh<=xb)and(yh>=ya and yh<=yb)):
				flag=True
			else:
				flag=False
		elif (cx>=0 and cy<=0):
			xh=xc+hx
			yh=yc+hy
			cc+=10
			if ((xh>=xa and xh<=xb)and(yh>=yb and yh<=ya)):
				flag=True
			else:
				flag=False
		elif (cx<=0 and cy<=0):
			xh=xc+hx
			yh=yc-hy
			cc+=100
			if ((xh>=xb and xh<=xa)and(yh>=yb and yh<=ya)):
				flag=True
			else:
				flag=False
		elif (cx<=0 and cy>=0):
			xh=xc-hx
			yh=yc-hy
			cc+=1000
			if ((xh>=xb and xh<=xa)and(yh>=ya and yh<=yb)):
				flag=True
			else:
				flag=False
		return h, flag
def holes_check(ind, xs, ys):
	flag=False
	for i in range(1, ind):
		if (xs[i]==xs[ind] and ys[i]==ys[ind]):
			flag=True
	return flag
def hole_id(ind, xs, ys):
	hid=0
	for i in range(1, ind):
		if (xs[i]==xs[ind] and ys[i]==ys[ind]):
			hid=i
	return hid
print('Step:')
step=float(input())
print('Processing...')
layer=shapefile.Reader("shapes/polygons")
shapes=layer.shapes()
xs=[]
ys=[]
stx=[]
sty=[]
holes=[]
holes_flags=[]
print('Reading polygons...')
for n in range(len(shapes)):
	xs.append([])
	ys.append([])
	stx.append(0)
	sty.append(0)
	holes.append([])
	holes_flags.append(False)
	for i in range(len(shapes[n].points)):
		xs[n].append(shapes[n].points[i][0])
		ys[n].append(shapes[n].points[i][1])
		if shapes[n].points[i][0]<shapes[n].points[stx[n]][0]:
			stx[n]=i
		if shapes[n].points[i][1]<shapes[n].points[sty[n]][1]:
			sty[n]=i
		if holes_check(i, xs[n], ys[n]):
			holes_flags[n]=True
			holes[n].append(hole_id(i, xs[n], ys[n]))
print('Done.')
print('Calculating distance grid...')
steps=[]
cc=0
ccc=0
for n in range(len(shapes)):
	steps.append([int((shapes[n].bbox[2]-xs[n][stx[n]])//step+1), int((shapes[n].bbox[3]-ys[n][sty[n]])//step+1)])
	cc+=steps[n][0]*steps[0][1]
ps=[]
xxs=[]
yys=[]
xis=[]
yis=[]
wrt=shapefile.Writer(shapeType=1)
wrt.field('id')
wrt.field('d', 'F', 100)
for n in range(len(shapes)):
	ps.append(numpy.empty([steps[n][0], steps[n][1]]))
	xxs.append(numpy.empty([steps[n][0], steps[n][1]]))
	yys.append(numpy.empty([steps[n][0], steps[n][1]]))
	x=xs[n][stx[n]]
	xis.append(0)
	yis.append(0)
	while x<shapes[n].bbox[2]:
		y=ys[n][sty[n]]
		yis[n]=0
		while y<shapes[n].bbox[3]:
			ccc+=1
			print(str(round(ccc*100/cc, 2)) + '% (' + str(ccc) + '/' + str(cc) + ')')
			if inPolygon(x, y, xs[n], ys[n], holes[n], holes_flags[n]):
				dflag=False
				d=0
				dm=-1
				for i in range(1, len(xs[n])):
					if not(i in holes[n]):
						d, dflag=triangle_altitude(xs[n][i-1], ys[n][i-1], xs[n][i], ys[n][i], x, y)
						if dflag:
							if dm==-1:
								dm=d
							elif d<dm:
								dm=d
						else:
							dn=math.sqrt((xs[n][0]-x)**2+(ys[n][0]-y)**2)
							for j in range(len(xs[n])):
								d=math.sqrt((xs[n][j]-x)**2+(ys[n][j]-y)**2)
								if d<dn:
									dn=d
							if dm==-1:
								dm=dn
							elif dn<dm:
								dm=dn
				ps[n][xis[n]][yis[n]]=dm
				xxs[n][xis[n]][yis[n]]=x
				yys[n][xis[n]][yis[n]]=y
				wrt.point(x, y)
				wrt.record('', round(dm, 2))
			else:
				ps[n][xis[n]][yis[n]]=0
				xxs[n][xis[n]][yis[n]]=x
				yys[n][xis[n]][yis[n]]=y
			y+=step
			yis[n]+=1
		x+=step
		xis[n]+=1
	name='test_img_'+str(n)+'.png'
	img=Image.new('RGBA', (steps[n][0], steps[n][1]), (0, 0, 0, 255))
	pix=img.load()
	fx=255/numpy.amax(ps[n])
	for i in range(steps[n][0]):
		for j in range(steps[n][1]):
			if not(ps[n][i][-j]==0):
				pix[i, j]=(255-int(ps[n][i][-j]*fx), 255-int(ps[n][i][-j]*fx), 255-int(ps[n][i][-j]*fx), 255)
	img.save(name, 'PNG')
wrt.save('shapes/distance_grid')
print('Done.')
print('Analyzing drainage...')
links=[]
for n in range(len(shapes)):
	links.append([])
	for i in range(steps[n][0]):
		links[n].append([])
		for j in range(steps[n][1]):
			links[n][i].append(0)
wrt2=shapefile.Writer(shapeType=1)
wrt2.field('id')
for n in range(len(shapes)):
	for i in range(steps[n][0]):
		for j in range(steps[n][1]):
			if not(ps[n][i][j]==0):
				if (i==0)and(j==0):
					wn=[[ps[n][i+1][j], [i+1, j]], [ps[n][i][j+1], [i, j+1]], [ps[n][i+1][j+1], [i+1, j+1]]]
				elif (i==0)and(j==steps[n][1]-1):
					wn=[[ps[n][i+1][j], [i+1, j]], [ps[n][i][j-1], [i, j-1]], [ps[n][i+1][j-1], [i+1, j-1]]]
				elif (i==steps[n][0]-1)and(j==0):
					wn=[[ps[n][i-1][j], [i-1, j]], [ps[n][i][j+1], [i, j+1]], [ps[n][i-1][j+1], [i-1, j+1]]]
				elif (i==steps[n][0]-1)and(j==steps[n][1]-1):
					wn=[[ps[n][i-1][j], [i-1, j]], [ps[n][i][j-1], [i, j-1]], [ps[n][i-1][j-1], [i-1, j-1]]]
				elif (i==0):
					wn=[[ps[n][i][j-1], [i, j-1]], [ps[n][i][j+1], [i, j+1]], [ps[n][i+1][j], [i+1, j]], [ps[n][i+1][j+1], [i+1, j+1]], [ps[n][i+1][j-1], [i+1, j-1]]]
				elif (i==steps[n][0]-1):
					wn=[[ps[n][i][j-1], [i, j-1]], [ps[n][i][j+1], [i, j+1]], [ps[n][i-1][j], [i-1, j]], [ps[n][i-1][j+1], [i-1, j+1]], [ps[n][i-1][j-1], [i-1, j-1]]]
				elif (j==0):
					wn=[[ps[n][i-1][j], [i-1, j]], [ps[n][i+1][j], [i+1, j]], [ps[n][i][j+1], [i, j+1]], [ps[n][i-1][j+1], [i-1, j+1]], [ps[n][i+1][j+1], [i+1, j+1]]]
				elif (j==steps[n][1]-1):
					wn=[[ps[n][i-1][j], [i-1, j]], [ps[n][i+1][j], [i+1, j]], [ps[n][i][j-1], [i, j-1]], [ps[n][i-1][j-1], [i-1, j-1]], [ps[n][i+1][j-1], [i+1, j-1]]]
				else:
					wn=[[ps[n][i+1][j], [i+1, j]], [ps[n][i][j+1], [i, j+1]], [ps[n][i-1][j], [i-1, j]], [ps[n][i][j-1], [i, j-1]], [ps[n][i+1][j+1], [i+1, j+1]], [ps[n][i-1][j+1], [i-1, j+1]], [ps[n][i+1][j-1], [i+1, j-1]], [ps[n][i-1][j-1], [i-1, j-1]]]
				wm=ps[n][i][j]
				wmi=[i, j]
				for wnm in wn:
					if wnm[0]>wm:
						wm=wnm[0]
						wmi=[wnm[1][0], wnm[1][1]]
				links[n][wmi[0]][wmi[1]]+=1
for n in range(len(shapes)):
	for i in range(steps[n][0]):
		for j in range(steps[n][1]):
			if links[n][i][j]>0:
				wrt2.point(xxs[n][i][j], yys[n][i][j])
				wrt2.record('')
wrt2.save('shapes/drainage_points')
print('Done.')
print('Have a nice day.')