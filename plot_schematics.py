"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)


def finite_executions(out):
    d=Drawing((0,0,14.6,7.9))
    d.text(.7,6.85,'Reference',8.5)
    items=[('h0',2,1.15,r'$h_{a-1}$'),('a',3.75,1.4,'Step a'),
           ('h1',5.45,1.1,r'$h_a$'),('b',7.15,1.45,'Step a+1'),
           ('h2',8.9,1.15,r'$h_{a+1}$'),('c',10.65,1.45,'Step a+2'),
           ('h3',12.45,1.2,r'$h_{a+2}$')]
    for name,x,w,label in items:d.box(name,x,6.85,w,.7,label,size=8.5)
    for a,b in zip(items,items[1:]):d.edge(a[0],b[0],'e','w')
    for x in (4.65,8.03,11.6):d.text(x,7.4,r'$Q$',8)
    d.text(.7,3.5,'Lowering',8.5)
    d.box('carry',2.5,3.5,1.75,.85,r'$\widehat h_{a-1}$',size=9)
    for i,(y,label,output) in enumerate([(5.1,r'$S_{a:a}$',r'$\widehat h_a$'),
                                        (3.5,r'$S_{a:a+1}$',r'$\widehat h_{a+1}$'),
                                        (1.9,r'$S_{a:a+2}$',r'$\widehat h_{a+2}$')]):
        d.box('s'+str(i),6.6,y,2.15,.8,label)
        d.box('o'+str(i),10.0,y,1.8,.8,output)
        d.edge('carry','s'+str(i),'e','w',via=((4.3,3.5),(4.3,y)))
        d.edge('s'+str(i),'o'+str(i),'e','w')
    d.arrow(d.point('o2','e'),(12.1,1.9))
    d.text(13.1,1.9,'Next carry',8.5)
    d.text(7.2,.65,r'Each summary uses quantized $\star$ nodes.',8.5)
    d.save(out,'finite-executions')

def ordered_cover(out):
    d=Drawing((0,0,14.2,7.4))
    d.box('root',6.6,6.3,5.5,1.2,
          '$B=\\{c,c+1\\}\\times\\{d,d+1\\}$\nSplit first varying $x_1$',size=9)
    d.box('left',2.8,3.9,4.0,1.05,'$x_1=c$\nSafe exact range',size=9)
    d.box('right',10.2,3.9,4.45,1.05,'$x_1=c+1$\nSplit first varying $x_2$',size=9)
    d.edge('root','left');d.edge('root','right')
    d.box('safe',7.5,1.6,3.3,1.05,'$x_2=d$\nSafe exact range',size=9)
    d.box('witness',12.15,1.6,3.5,1.05,'$x_2=d+1$: singleton\nReplay violates',size=9)
    d.edge('right','safe');d.edge('right','witness')
    d.text(3.1,1.55,'Lower children precede\nupper children.',8.5)
    d.text(7.1,.45,'Earlier outputs have separate safe roots.',8.5)
    d.save(out,'ordered-cover')

def rounding_annihilator(out):
    d=Drawing((0,0,14.6,6.8))
    d.box('input',1.65,5.25,2.45,1.15,'$x\\in\\{0,1\\}$\n$s=0$',size=9)
    d.box('a',5.1,5.25,3.45,1.65,'Step $A$\n$x\\leftarrow x$\n$s\\leftarrow R_2(x)$',size=9)
    d.box('c',9.05,5.25,3.45,1.65,'Step $C$\n$x\\leftarrow R_2(2x-4s)$',size=8.5)
    d.box('seq',12.65,5.25,2.5,1.15,'Sequential\n$x^\\prime=x$',size=9)
    d.edge('input','a','e','w');d.edge('a','c','e','w');d.edge('c','seq','e','w')
    d.box('sum',8.15,2.1,5.4,1.3,'Quantized summary $A\\star C$\nOutput row = (0, 0)',size=9)
    d.box('low',12.65,2.1,2.5,1.15,'Lowered\n$\\widehat x^\\prime=0$',size=9)
    d.edge('input','sum','s','w',via=((1.65,2.1),))
    d.edge('sum','low','e','w')
    d.text(7.3,.65,'Scale 2; floor or nearest-even; no active clipping.',8.5)
    d.save(out,'rounding-annihilator')

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    finite_executions(args.outdir);ordered_cover(args.outdir);rounding_annihilator(args.outdir)
if __name__=='__main__':main()
