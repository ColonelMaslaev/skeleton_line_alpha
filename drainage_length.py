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
print('Step (units):')
step=float(input())
print('Threshold (%):')
thres=float(input())
print('Processing...')
layer=shapefile.Reader("shapes/polygons_max_length")
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
	cc+=steps[n][0]*steps[n][1]
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
	#name='test_img_'+str(n)+'.png'
	#img=Image.new('RGBA', (steps[n][0], steps[n][1]), (0, 0, 0, 255))
	#pix=img.load()
	#fx=255/numpy.amax(ps[n])
	#for i in range(steps[n][0]):
	#	for j in range(steps[n][1]):
	#		if not(ps[n][i][-j]==0):
	#			pix[i, j]=(255-int(ps[n][i][-j]*fx), 255-int(ps[n][i][-j]*fx), 255-int(ps[n][i][-j]*fx), 255)
	#img.save(name, 'PNG')
wrt.save('shapes/distance_grid_ml')
print('Done.')
print('Analyzing drainage...')
wrt2=shapefile.Writer(shapeType=1)
wrt2.field('id')
wrt2.field('d', 'F', 100)
wrt2.field('i', 'F', 100)
wrt2.field('j', 'F', 100)
wrt2.field('cc', 'F', 100)
wrt2.field('cl', 'F', 100)
wrt2.field('n', 'F', 100)
drpt=[]
dept=[]
for n in range(len(shapes)):
	wwn=0
	drpt.append([])
	dept.append([-1, -1])
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
				wms=0
				for wnm in wn:
					if (abs(i-wnm[1][0])+abs(j-wnm[1][1]))<2:
						wms+=ps[n][i][j]-wnm[0]
				if wms>(step*thres/100):
					drpt[n].append([ps[n][i][j], [i, j], wms, [], 0, wwn])
					if drpt[n][wwn][0]>dept[n][0]:
						dept[n]=[drpt[n][wwn][0], wwn]
					wwn+=1
print('Done.')
print('Constructing skeleton lines...')
lineswrt=shapefile.Writer(shapeType=3)
lineswrt.field('id')
lineswrt.field('l', 'F', 100)
clusters=[]
graph_links=[]
lines=[]
ext_lines=[]
for n in range(len(shapes)):
	clusters.append([])
	graph_links.append([])
	ext_lines.append([])
	for w in drpt[n]:
		i=w[1][0]
		j=w[1][1]
		wn=[]
		for ww in drpt[n]:
			if ww==0:
				continue
			if not(w==ww):
				iw=ww[1][0]
				jw=ww[1][1]
				#if (((abs(i-iw)==1)and(j==jw))or((abs(j-jw)==1)and(i==iw))or((abs(i-iw)==1)and(abs(j-jw)==1))):
				#	wn.append(ww)
				if (i-iw==1)and(j-jw==1):
					wn.append(ww)
				if (i-iw==1)and(j-jw==0):
					wn.append(ww)
				if (i-iw==1)and(j-jw==-1):
					wn.append(ww)
				if (i-iw==0)and(j-jw==1):
					wn.append(ww)
				if (i-iw==0)and(j-jw==-1):
					wn.append(ww)
				if (i-iw==-1)and(j-jw==1):
					wn.append(ww)
				if (i-iw==-1)and(j-jw==0):
					wn.append(ww)
				if (i-iw==-1)and(j-jw==-1):
					wn.append(ww)
		if wn==[]:
			drpt[n][w[5]]=[-1, [-1, -1], -1, [], 2, w[5], [], -1]
		else:
			wm=w
			drpt[n][w[5]].append([])
			for wmn in wn:
				drpt[n][w[5]][6].append(wmn[5])
				if wmn[0]>wm[0]:
					wm=wmn
			if not(wm==w):
				drpt[n][w[5]][3].append(wm[5])
				drpt[n][wm[5]][3].append(w[5])
				#if not([[xxs[n][i][j], yys[n][i][j]], [xxs[n][wm[1][0]][wm[1][1]], yys[n][wm[1][0]][wm[1][1]]]] in lines):
					#if not([[xxs[n][wm[1][0]][wm[1][1]], yys[n][wm[1][0]][wm[1][1]]], [xxs[n][i][j], yys[n][i][j]]] in lines):
						#lines.append([[xxs[n][i][j], yys[n][i][j]], [xxs[n][wm[1][0]][wm[1][1]], yys[n][wm[1][0]][wm[1][1]]]])
	cl=0
	#drpt: [d, [i, j], cc, [linked_ids], graph_status, id, [neighbors_ids], cluster_id]
	for w in drpt[n]:
		if w==0:
			continue
		if w[4]==0:
			clusters[n].append([w[5]])
			drpt[n][w[5]][4]=1
			drpt[n][w[5]].append(cl)
			graph_flag=True
			while graph_flag:
				graph_flag=False
				for ws in clusters[n][cl]:
					if drpt[n][ws][4]==1:
						for wws in drpt[n][ws][3]:
							if drpt[n][wws][4]==0:
								clusters[n][cl].append(wws)
								drpt[n][wws][4]=1
								drpt[n][wws].append(cl) 
								graph_flag=True
						drpt[n][ws][4]=2
			cl+=1
	for cluster in clusters[n]:
		for wi in cluster:
			for wni in drpt[n][wi][6]:
				if not(drpt[n][wi][7]==drpt[n][wni][7]):
					if not(([drpt[n][wi][7], drpt[n][wni][7], []] in graph_links[n])or([drpt[n][wni][7], drpt[n][wi][7], []] in graph_links[n])):
						graph_links[n].append([drpt[n][wi][7], drpt[n][wni][7], []])
	link_count=0
	for link in graph_links[n]:
		for wi in clusters[n][link[0]]:
			for wni in drpt[n][wi][6]:
				if drpt[n][wni][7]==link[1]:
					graph_links[n][link_count][2].append(wi)
					break
		for wi in clusters[n][link[1]]:
			for wni in drpt[n][wi][6]:
				if drpt[n][wni][7]==link[0]:
					graph_links[n][link_count][2].append(wi)
					break
		wip=[0]
		for wi in graph_links[n][link_count][2]:
			if drpt[n][wi][0]>wip[0]:
				wip=drpt[n][wi]
		wip2=[0]
		if wip[7]==link[0]:
			act_link=link[1]
		else:
			act_link=link[0]
		for wi in wip[6]:
			if drpt[n][wi][7]==act_link:
				if drpt[n][wi][0]>wip2[0]:
					wip2=drpt[n][wi]
		#lines.append([[xxs[n][wip[1][0]][wip[1][1]], yys[n][wip[1][0]][wip[1][1]]], [xxs[n][wip2[1][0]][wip2[1][1]], yys[n][wip2[1][0]][wip2[1][1]]]])
		drpt[n][wip[5]][3].append(wip2[5])
		drpt[n][wip2[5]][3].append(wip[5])
		link_count+=1
	wd=dept[n][1]
	sel_points=[wd]
	drpt[n][wd][4]=3
	dept_flag=True
	while dept_flag:
		dept_flag=False
		for ws in sel_points:
			if drpt[n][ws][4]==3:
				for wws in drpt[n][ws][3]:
					if drpt[n][wws][4]==2:
						sel_points.append(wws)
						drpt[n][wws][4]=3
						dept_flag=True
				drpt[n][ws][4]=4
	for w in drpt[n]:
		if (w[4]==2):
			drpt[n][w[5]][3]=[]
	thin_flag=True
	while thin_flag:
		thin_flag=False
		for w in drpt[n]:
			if len(w[3])==1:
				if len(w[6])>1:
					thin_flag=True
					drpt[n][w[3][0]][3].remove(w[5])
					for ws in w[6]:
						drpt[n][ws][6].remove(w[5])
					drpt[n][w[5]][3]=[]
					break
	for w in drpt[n]:
		for wws in w[3]:
			ws=drpt[n][wws]
			dw=math.sqrt((xxs[n][w[1][0]][w[1][1]]-xxs[n][ws[1][0]][ws[1][1]])**2+(yys[n][w[1][0]][w[1][1]]-yys[n][ws[1][0]][ws[1][1]])**2)
			if not([[[xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]], [xxs[n][ws[1][0]][ws[1][1]], yys[n][ws[1][0]][ws[1][1]]]], dw] in lines):
				if not([[[xxs[n][ws[1][0]][ws[1][1]], yys[n][ws[1][0]][ws[1][1]]], [xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]]], dw] in lines):
					lines.append([[[xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]], [xxs[n][ws[1][0]][ws[1][1]], yys[n][ws[1][0]][ws[1][1]]]], dw])
		if len(w[3])==1:
			dw=[math.sqrt((xxs[n][w[1][0]][w[1][1]]-xs[n][0])**2+(yys[n][w[1][0]][w[1][1]]-ys[n][0])**2), 0]
			for nw in range(len(xs[n])):
				dww=[math.sqrt((xxs[n][w[1][0]][w[1][1]]-xs[n][nw])**2+(yys[n][w[1][0]][w[1][1]]-ys[n][nw])**2), nw]
				if dww[0]<dw[0]:
					dw=dww
			lines.append([[[xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]], [xs[n][dw[1]], ys[n][dw[1]]]], dw[0]])
	exn=0
	for w in drpt[n]:
		if (len(w[3])==1)and(w[4]==4):
			ext_lines[n].append([])
			drpt[n][w[5]][4]=5
			dw=[math.sqrt((xxs[n][w[1][0]][w[1][1]]-xs[n][0])**2+(yys[n][w[1][0]][w[1][1]]-ys[n][0])**2), 0]
			for nw in range(len(xs[n])):
				dww=[math.sqrt((xxs[n][w[1][0]][w[1][1]]-xs[n][nw])**2+(yys[n][w[1][0]][w[1][1]]-ys[n][nw])**2), nw]
				if dww[0]<dw[0]:
					dw=dww
			ext_lines[n][exn].append([[xs[n][dw[1]], ys[n][dw[1]]], [xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]]])
			dw=dw[0]
			ext_lines[n][exn][0].append([xxs[n][drpt[n][w[3][0]][1][0]][drpt[n][w[3][0]][1][1]], yys[n][drpt[n][w[3][0]][1][0]][drpt[n][w[3][0]][1][1]]])
			dw+=math.sqrt((xxs[n][w[1][0]][w[1][1]]-xxs[n][drpt[n][w[3][0]][1][0]][drpt[n][w[3][0]][1][1]])**2+(yys[n][w[1][0]][w[1][1]]-yys[n][drpt[n][w[3][0]][1][0]][drpt[n][w[3][0]][1][1]])**2)
			ext_flag=True
			ec=w[3][0]
			while ext_flag:
				if len(drpt[n][ec][3])==2:
					drpt[n][ec][4]=5
					if drpt[n][drpt[n][ec][3][0]][4]==4:
						ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
						dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
						ec=drpt[n][ec][3][0]
					else:
						ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]], yys[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]]])
						dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][0]])**2)
						ec=drpt[n][ec][3][1]
				if len(drpt[n][ec][3])==1:
					ext_flag=False
					drpt[n][ec][4]=5
					ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
					dwt=[math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xs[n][0])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-ys[n][0])**2), 0]
					for nw in range(len(xs[n])):
						dww=[math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xs[n][nw])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-ys[n][nw])**2), nw]
						if dww[0]<dwt[0]:
							dwt=dww
					ext_lines[n][exn].append([[xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]], yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]], [xs[n][dw[1]], ys[n][dw[1]]]])
					dw+=dwt
					ext_lines[n][exn].append(0)
					dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
					ext_lines[n][exn].append(dw)
					ext_lines[n][exn].append(w[5])
					ext_lines[n][exn].append(ec)
				if len(drpt[n][ec][3])==3:
					ext_flag=False
					ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
					ext_lines[n][exn].append(1)
					dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
					ext_lines[n][exn].append(dw)
					ext_lines[n][exn].append(w[5])
					ext_lines[n][exn].append(ec)
			exn+=1
		if (len(w[3])==3)and(w[4]==4):
			if (drpt[n][w[3][0]][4]==5)and(drpt[n][w[3][1]][4]==5)and(drpt[n][w[3][2]][4]==5):
				drpt[n][w[5]][4]=5
			else:
				for wsn in w[3]:
					if drpt[n][wsn][4]==4:
						ext_lines[n].append([])
						dw=math.sqrt((xxs[n][w[1][0]][w[1][1]]-xxs[n][drpt[n][wsn][1][0]][drpt[n][wsn][1][1]])**2+(yys[n][w[1][0]][w[1][1]]-yys[n][drpt[n][wsn][1][0]][drpt[n][wsn][1][1]])**2)
						ext_lines[n][exn].append([[xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]]], [xxs[n][drpt[n][wsn][1][0]][drpt[n][wsn][1][1]], yys[n][drpt[n][wsn][1][0]][drpt[n][wsn][1][1]]]])
						drpt[n][wsn][4]=5
						ext_flag=True
						ec=wsn
						while ext_flag:
							if len(drpt[n][ec][3])==2:
								drpt[n][ec][4]=5
								if drpt[n][drpt[n][ec][3][0]][4]==4:
									ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
									dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
									ec=drpt[n][ec][3][0]
								else:
									ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]], yys[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]]])
									dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][1]][1][0]][drpt[n][drpt[n][ec][3][1]][1][0]])**2)
									ec=drpt[n][ec][3][1]
							if len(drpt[n][ec][3])==1:
								ext_flag=False
								drpt[n][ec][4]=5
								ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
								dwt=[math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xs[n][0])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-ys[n][0])**2), 0]
								for nw in range(len(xs[n])):
									dww=[math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xs[n][nw])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-ys[n][nw])**2), nw]
									if dww[0]<dwt[0]:
										dwt=dww
								ext_lines[n][exn].append([[xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]], yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]], [xs[n][dwt[1]], ys[n][dwt[1]]]])
								dw+=dwt[0]
								dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
								ext_lines[n][exn].append(1)
								ext_lines[n][exn].append(dw)
								ext_lines[n][exn].append(w[5])
								ext_lines[n][exn].append(ec)
							if len(drpt[n][ec][3])==3:
								ext_flag=False
								ext_lines[n][exn][0].append([xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]], yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]]])
								dw+=math.sqrt((xxs[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-xxs[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][1]])**2+(yys[n][drpt[n][ec][1][0]][drpt[n][ec][1][1]]-yys[n][drpt[n][drpt[n][ec][3][0]][1][0]][drpt[n][drpt[n][ec][3][0]][1][0]])**2)
								ext_lines[n][exn].append(2)
								ext_lines[n][exn].append(dw)
								ext_lines[n][exn].append(w[5])
								ext_lines[n][exn].append(ec)
						exn+=1
	for lin in ext_lines[n]:
		lineswrt.line(parts=[lin[0]])
		lineswrt.record('', lin[2])
for n in range(len(shapes)):
	for w in drpt[n]:
		if w==[-1, [-1, -1], -1, [], 2, w[5], [], -1]:
			continue
		wrt2.point(xxs[n][w[1][0]][w[1][1]], yys[n][w[1][0]][w[1][1]])
		wrt2.record('', round(w[0], 2), float(w[1][0]), float(w[1][1]), w[2], w[7], w[5])
wrt2.save('shapes/drainage_points_ml')
lineswrt.save('shapes/drainage_links_ml')
print('Done.')
print('Have a nice day.')