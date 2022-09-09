import shapefile
import math
import numpy
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
def triangle_check(a, b, c, xc, yc, xs, ys, hs, hflag, dbls):
	r=math.sqrt((xc-xs[a])**2+(yc-ys[a])**2)
	flag=True
	for i in range(len(xs)):
		if not(i==a or i==b or i==c or (i in dbls)):
			ri=math.sqrt((xc-xs[i])**2+(yc-ys[i])**2)
			if ri<r:
				#if not(intersection_check(xs[a], ys[a], xs[i], ys[i], xs, ys, hs)):
					#continue
				#if not(intersection_check(xs[b], ys[b], xs[i], ys[i], xs, ys, hs)):
					#continue
				#if not(intersection_check(xs[c], ys[c], xs[i], ys[i], xs, ys, hs)):
					#continue
				#if not(inPolygon((xs[a]+xs[i])/2, (ys[a]+ys[i])/2, xs, ys, hs, hflag)):
					#continue
				#if not(inPolygon((xs[b]+xs[i])/2, (ys[b]+ys[i])/2, xs, ys, hs, hflag)):
					#continue
				#if not(inPolygon((xs[c]+xs[i])/2, (ys[c]+ys[i])/2, xs, ys, hs, hflag)):
					#continue
				flag=False
				break
	return flag
def intersection_check(x1, y1, x2, y2, xs, ys, hs): #check neighbors
	flag=True
	for i in range(len(xs)-1):
		if not((i+1) in hs):
			v1=(xs[i+1]-xs[i])*(y1-ys[i])-(ys[i+1]-ys[i])*(x1-xs[i])
			v2=(xs[i+1]-xs[i])*(y2-ys[i])-(ys[i+1]-ys[i])*(x2-xs[i])
			v3=(x2-x1)*(ys[i]-y1)-(y2-y1)*(xs[i]-x1)
			v4=(x2-x1)*(ys[i+1]-y1)-(y2-y1)*(xs[i+1]-x1)
			if (v1*v2<0 and v3*v4<0):
				flag=False
				break
	return flag
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
def angle_check(a, b, c):
	flag=False
	cosa=(b*b+c*c-a*a)/(2*b*c)
	if cosa<=0:
		flag=True
	return flag
layer=shapefile.Reader("shapes/polygons")
shapes=layer.shapes()
ccc=0
xs=[]
ys=[]
neigh=[]
doubles=[]
holes=[]
holes_flags=[]
print('Reading polygons...')
for n in range(len(shapes)):
	xs.append([])
	ys.append([])
	holes.append([])
	neigh.append([])
	doubles.append([])
	holes_flags.append(False)
	for i in range(len(shapes[n].points)):
		xs[n].append(shapes[n].points[i][0])
		ys[n].append(shapes[n].points[i][1])
		if holes_check(i, xs[n], ys[n]):
			holes_flags[n]=True
			holes[n].append(hole_id(i, xs[n], ys[n]))
			neigh[n].append([hole_id(i, xs[n], ys[n]), i-1])
			doubles[n].append(i)
	if holes_flags[n]:
		neigh[n].append([0, (holes[n][0]-2)])
		doubles[n].append(holes[n][0]-1)
	else:
		neigh[n].append([0, (len(shapes[n].points)-2)])
		doubles[n].append(len(shapes[n].points)-1)
print('Done.')
print('Building Delaunay triangulation...')
#print(neigh[0])
ccc=0
iterations=0
for n in range(len(shapes)):
	iterations+=(len(xs[n]))**3
lines=[]
lnids=[]
triangles=[]
processed=[]
for n in range(len(shapes)):
	for a in range(len(xs[n])):
		for b in range(len(xs[n])):
			for c in range(len(xs[n])):
				ccc+=1
				print(round((ccc/iterations)*100, 4), '%', ccc, iterations)
				if not(a==b or a==c or b==c or (a in doubles[n]) or (b in doubles[n]) or (c in doubles[n])):
					if (a>b and a>c):
						if b>c:
							i1, i2, i3=c, b, a
						else:
							i1, i2, i3=b, c, a
					elif (a>b and a<c):
						i1, i2, i3=b, a, c
					elif (a>c and a<b):
						i1, i2, i3=c, a, b
					else:
						if b>c:
							i1, i2, i3=a, c, b
						else:
							i1, i2, i3=a, b, c
					if ([i1, i2, i3] in processed):
						continue
					else:
						processed.append([i1, i2, i3])
					#print(i1, i2, i3)
					d=2*(xs[n][i1]*(ys[n][i2]-ys[n][i3])+xs[n][i2]*(ys[n][i3]-ys[n][i1])+xs[n][i3]*(ys[n][i1]-ys[n][i2]))
					if d==0:
						#print('--------')
						continue
					ac=numpy.linalg.det(numpy.array([[xs[n][i1], ys[n][i1], 1], [xs[n][i2], ys[n][i2], 1], [xs[n][i3], ys[n][i3], 1]]))
					bc=numpy.linalg.det(numpy.array([[(xs[n][i1]**2+ys[n][i1]**2), ys[n][i1], 1], [(xs[n][i2]**2+ys[n][i2]**2), ys[n][i2], 1], [(xs[n][i3]**2+ys[n][i3]**2), ys[n][i3], 1]]))
					cc=numpy.linalg.det(numpy.array([[(xs[n][i1]**2+ys[n][i1]**2), xs[n][i1], 1], [(xs[n][i2]**2+ys[n][i2]**2), xs[n][i2], 1], [(xs[n][i3]**2+ys[n][i3]**2), xs[n][i3], 1]]))
					if ac==0:
						continue
					xc=bc/(2*ac)
					yc=-(cc/(2*ac))
					#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
						#print(i1, i2, i3)
						#print(triangle_check(i1, i2, i3, xc, yc, xs[n], ys[n], holes[n], holes_flags[n], doubles[n]))
						#print(xc, yc, d, ac)
					#xc=((xs[n][i1]**2+ys[n][i1]**2)*(ys[n][i2]-ys[n][i3])+(xs[n][i2]**2+ys[n][i2]**2)*(ys[n][i3]-ys[n][i1])+(xs[n][i3]**2+ys[n][i3]**2)*(ys[n][i1]-ys[n][i3]))/d
					#yc=((xs[n][i1]**2+ys[n][i1]**2)*(xs[n][i3]-xs[n][i2])+(xs[n][i2]**2+ys[n][i2]**2)*(xs[n][i1]-xs[n][i3])+(xs[n][i3]**2+ys[n][i3]**2)*(xs[n][i2]-xs[n][i1]))/d
					#print(xc, yc, triangle_check(i1, i2, i3, xc, yc, xs[n], ys[n]))
					if not(triangle_check(i1, i2, i3, xc, yc, xs[n], ys[n], holes[n], holes_flags[n], doubles[n])):
						#print('--------')
						continue
					if (((i1==i2-1)and(not(i2 in holes[n])))and((i2==i3-1)and(not(i3 in holes[n])))):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('1')
						if (intersection_check(xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i1, i3] in lnids)or([i3, i1] in lnids)):
							lines.append([xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3]])
								#lnids.append([i1, i3])
							triangles.append([0, xs[n][i2], ys[n][i2], (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2])
							#print([xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3]])
							#print(0, xs[n][i2], ys[n][i2], (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2)
							#print('--------')
					elif (([i1, i3] in neigh[n])and(i1==i2-1)):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('2')
						if (intersection_check(xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i2, i3] in lnids)or([i3, i2] in lnids)):
							lines.append([xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3]])
								#lnids.append([i2, i3])
							triangles.append([0, xs[n][i1], ys[n][i1], (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2])
							#print([xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3]])
							#print(0, xs[n][i1], ys[n][i1], (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2)
							#print('--------')
					elif (([i1, i3] in neigh[n])and(i2==i3-1)):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('3')
						if (intersection_check(xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i1, i2] in lnids)or([i2, i1] in lnids)):
							lines.append([xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2]])
								#lnids.append([i1, i2])
							triangles.append([0, xs[n][i3], ys[n][i3], (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2])
							#print([xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2]])
							#print(0, xs[n][i3], ys[n][i3], (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2)
							#print('--------')
					elif ((i1==i2-1)and(not(i2 in holes[n])))or([i1, i2] in neigh[n]):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('4')
						if (intersection_check(xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(intersection_check(xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n]))and(inPolygon((xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i1, i3] in lnids)or([i3, i1] in lnids)):
							lines.append([xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3]])
								#lnids.append([i1, i3])
							#if not(([i2, i3] in lnids)or([i3, i2] in lnids)):
							lines.append([xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3]])
								#lnids.append([i2, i3])
							triangles.append([1, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2])
							#print([xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3]])
							#print([xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3]])
							#print(1, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2)
							#print('--------')
					elif ((i2==i3-1)and(not(i3 in holes[n])))or([i2, i3] in neigh[n]):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('5')
						if (intersection_check(xs[n][i2], ys[n][i2], xs[n][i1], ys[n][i1], xs[n], ys[n], holes[n]))and(intersection_check(xs[n][i3], ys[n][i3], xs[n][i1], ys[n][i1], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, xs[n], ys[n], holes[n], holes_flags[n]))and(inPolygon((xs[n][i3]+xs[n][i1])/2, (ys[n][i3]+ys[n][i1])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i2, i1] in lnids)or([i1, i2] in lnids)):
							lines.append([xs[n][i2], ys[n][i2], xs[n][i1], ys[n][i1]])
								#lnids.append([i2, i1])
							#if not(([i3, i1] in lnids)or([i1, i3] in lnids)):
							lines.append([xs[n][i3], ys[n][i3], xs[n][i1], ys[n][i1]])
								#lnids.append([i3, i1])
							triangles.append([1, (xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, (xs[n][i3]+xs[n][i1])/2, (ys[n][i3]+ys[n][i1])/2])
							#print([xs[n][i2], ys[n][i2], xs[n][i1], ys[n][i1]])
							#print([xs[n][i3], ys[n][i3], xs[n][i1], ys[n][i1]])
							#print(1, (xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, (xs[n][i3]+xs[n][i1])/2, (ys[n][i3]+ys[n][i1])/2)
							#print('--------')
					elif ((i1==i3-1)and(not(i3 in holes[n])))or([i1, i3] in neigh[n]):
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('6')
						if (intersection_check(xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2], xs[n], ys[n], holes[n]))and(intersection_check(xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, xs[n], ys[n], holes[n], holes_flags[n]))and(inPolygon((xs[n][i3]+xs[n][i2])/2, (ys[n][i3]+ys[n][i2])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							#if not(([i2, i1] in lnids)or([i1, i2] in lnids)):
							lines.append([xs[n][i2], ys[n][i2], xs[n][i1], ys[n][i1]])
								#lnids.append([i2, i1])
							#if not(([i3, i1] in lnids)or([i1, i3] in lnids)):
							lines.append([xs[n][i3], ys[n][i3], xs[n][i2], ys[n][i2]])
								#lnids.append([i3, i1])
							triangles.append([1, (xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, (xs[n][i3]+xs[n][i2])/2, (ys[n][i3]+ys[n][i2])/2])
							#print([xs[n][i2], ys[n][i2], xs[n][i1], ys[n][i1]])
							#print([xs[n][i3], ys[n][i3], xs[n][i1], ys[n][i1]])
							#print(1, (xs[n][i2]+xs[n][i1])/2, (ys[n][i2]+ys[n][i1])/2, (xs[n][i3]+xs[n][i1])/2, (ys[n][i3]+ys[n][i1])/2)
							#print('--------')
					else:
						#if (i1==0 and i2==1 and i3==36)or(i1==1 and i2==2 and i3==36)or(i1==0 and i2==36 and i3==37):
								#print('7')
						if (intersection_check(xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2], xs[n], ys[n], holes[n]))and(intersection_check(xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(intersection_check(xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3], xs[n], ys[n], holes[n]))and(inPolygon((xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, xs[n], ys[n], holes[n], holes_flags[n]))and(inPolygon((xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n]))and(inPolygon((xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, xs[n], ys[n], holes[n], holes_flags[n])):
							if angle_check(math.sqrt((xs[n][i1]-xs[n][i2])**2+(ys[n][i1]-ys[n][i2])**2), math.sqrt((xs[n][i1]-xs[n][i3])**2+(ys[n][i1]-ys[n][i3])**2), math.sqrt((xs[n][i2]-xs[n][i3])**2+(ys[n][i2]-ys[n][i3])**2)):
								triangles.append([2, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2])
							elif angle_check(math.sqrt((xs[n][i1]-xs[n][i3])**2+(ys[n][i1]-ys[n][i3])**2), math.sqrt((xs[n][i1]-xs[n][i2])**2+(ys[n][i1]-ys[n][i2])**2), math.sqrt((xs[n][i2]-xs[n][i3])**2+(ys[n][i2]-ys[n][i3])**2)):
								triangles.append([2, (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2])
							elif angle_check(math.sqrt((xs[n][i2]-xs[n][i3])**2+(ys[n][i2]-ys[n][i3])**2), math.sqrt((xs[n][i1]-xs[n][i2])**2+(ys[n][i1]-ys[n][i2])**2), math.sqrt((xs[n][i1]-xs[n][i3])**2+(ys[n][i1]-ys[n][i3])**2)):
								triangles.append([2, (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2])
							else:
								triangles.append([3, (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2, xc, yc])
							#if not(([i1, i2] in lnids)or([i2, i1] in lnids)):
							lines.append([xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2]])
								#lnids.append([i1, i2])
							#if not(([i1, i3] in lnids)or([i3, i1] in lnids)):
							lines.append([xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3]])
								#lnids.append([i1, i3])
							#if not(([i2, i3] in lnids)or([i3, i2] in lnids)):
							lines.append([xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3]])
								#lnids.append([i2, i3])
							#print(n, a, b, c)
							#print(xs[n][i1], ys[n][i1], xs[n][i2], ys[n][i2])
							#print(xs[n][i1], ys[n][i1], xs[n][i3], ys[n][i3])
							#print(xs[n][i2], ys[n][i2], xs[n][i3], ys[n][i3])
							#print(2, (xs[n][i1]+xs[n][i2])/2, (ys[n][i1]+ys[n][i2])/2, (xs[n][i1]+xs[n][i3])/2, (ys[n][i1]+ys[n][i3])/2, (xs[n][i2]+xs[n][i3])/2, (ys[n][i2]+ys[n][i3])/2)
							#print('--------')
print('Done.')
print('Constructing skeleton lines...')
#for i in triangles:
	#print(i)
lineswrt=shapefile.Writer(shapeType=3)
lineswrt.field('id')
for i in range(len(lines)):
	lineswrt.line(parts=[[[lines[i][0], lines[i][1]], [lines[i][2], lines[i][3]]]])
	lineswrt.record(i)
lineswrt.save('shapes/inner_triangulation')
skeletonwrt=shapefile.Writer(shapeType=3)
skeletonwrt.field('id')
for i in range(len(triangles)):
	if triangles[i][0]==2:
		skeletonwrt.line(parts=[[[triangles[i][5], triangles[i][6]], [triangles[i][1], triangles[i][2]]]])
		skeletonwrt.record(i)
		skeletonwrt.line(parts=[[[triangles[i][5], triangles[i][6]], [triangles[i][3], triangles[i][4]]]])
		skeletonwrt.record(i)
	elif triangles[i][0]==3:
		skeletonwrt.line(parts=[[[triangles[i][7], triangles[i][8]], [triangles[i][1], triangles[i][2]]]])
		skeletonwrt.record(i)
		skeletonwrt.line(parts=[[[triangles[i][7], triangles[i][8]], [triangles[i][3], triangles[i][4]]]])
		skeletonwrt.record(i)
		skeletonwrt.line(parts=[[[triangles[i][7], triangles[i][8]], [triangles[i][5], triangles[i][6]]]])
		skeletonwrt.record(i)
	else:
		skeletonwrt.line(parts=[[[triangles[i][1], triangles[i][2]], [triangles[i][3], triangles[i][4]]]])
		skeletonwrt.record(i)
skeletonwrt.save('shapes/skeleton_lines')
print('Done.')
print('Have a nice day.')