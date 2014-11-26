#!/usr/bin/env python 
'''
Copyright (C) 2005,2007 Aaron Spike, aaron@ekips.org
- template dxf_outlines.dxf added Feb 2008 by Alvin Penner, penner@vaxxine.com
- layers, transformation, flattening added April 2008 by Bob Cook, bob@bobcookdev.com
- bug fix for xpath() calls added February 2009 by Bob Cook, bob@bobcookdev.com
- max value of 10 on path flattening, August 2011 by Bob Cook, bob@bobcookdev.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''
import inkex, simplepath, simpletransform, cubicsuperpath, cspsubdiv, dxf_templates, re

class MyEffect(inkex.Effect):

    def __init__(self):
    
        inkex.Effect.__init__(self)
        self.dxf = ''
        self.handle = 255
        self.flatness = 0.1
        
    def output(self):
        print self.dxf
        
    def dxf_add(self, str):
        self.dxf += str
        
    def dxf_insert_code(self, code, value):
        self.dxf += code + "\n" + value + "\n"
        
    def dxf_line(self,layer,csp):
        self.dxf_insert_code(   '0', 'LINE' )
        self.dxf_insert_code(   '8', layer )
        self.dxf_insert_code(  '62', '4' )
        self.dxf_insert_code(   '5', '%x' % self.handle )
        self.dxf_insert_code( '100', 'AcDbEntity' )
        self.dxf_insert_code( '100', 'AcDbLine' )
        self.dxf_insert_code(  '10', '%f' % csp[0][0] )
        self.dxf_insert_code(  '20', '%f' % csp[0][1] )
        self.dxf_insert_code(  '30', '0.0' )
        self.dxf_insert_code(  '11', '%f' % csp[1][0] )
        self.dxf_insert_code(  '21', '%f' % csp[1][1] )
        self.dxf_insert_code(  '31', '0.0' )
        
    def dxf_point(self,layer,x,y):
        self.dxf_insert_code(   '0', 'POINT' )
        self.dxf_insert_code(   '8', layer )
        self.dxf_insert_code(  '62', '4' )
        self.dxf_insert_code(   '5', '%x' % self.handle )
        self.dxf_insert_code( '100', 'AcDbEntity' )
        self.dxf_insert_code( '100', 'AcDbPoint' )
        self.dxf_insert_code(  '10', '%f' % x )
        self.dxf_insert_code(  '20', '%f' % y )
        self.dxf_insert_code(  '30', '0.0' )
        
    def dxf_path_to_lines(self,layer,p):
        f = self.flatness
        is_flat = 0
        while is_flat < 1:
            if f > 10:
                break
            try:
                cspsubdiv.cspsubdiv(p, f)
                is_flat = 1
            except:
                f += 0.1
        
        for sub in p:
            for i in range(len(sub)-1):
                self.handle += 1
                s = sub[i]
                e = sub[i+1]
                self.dxf_line(layer,[s[1],e[1]])
    
    def dxf_path_to_point(self,layer,p):
        bbox = simpletransform.roughBBox(p)
        x = (bbox[0] + bbox[1]) / 2
        y = (bbox[2] + bbox[3]) / 2
        self.dxf_point(layer,x,y)
        
    def effect(self):
        self.dxf_insert_code( '999', 'Inkscape export via "Better DXF Output" (bob@bobcookdev.com)' )
        self.dxf_add( dxf_templates.r14_header )
        
        scale = 25.4/90.0
        h = inkex.unittouu(self.document.getroot().xpath('@height',namespaces=inkex.NSS)[0])
        
        path = '//svg:path'
        for node in self.document.getroot().xpath(path,namespaces=inkex.NSS):
        
            layer = node.getparent().get(inkex.addNS('label','inkscape'))
            if layer == None:
                layer = 'Layer 1'
            
            d = node.get('d')
            p = cubicsuperpath.parsePath(d)
            
            t = node.get('transform')
            if t != None:
                m = simpletransform.parseTransform(t)
                simpletransform.applyTransformToPath(m,p)
            
            m = [[scale,0,0],[0,-scale,h*scale]]
            simpletransform.applyTransformToPath(m,p)
    
            if re.search('drill$',layer,re.I) == None:
                self.dxf_path_to_lines(layer,p)
            else:    
                self.dxf_path_to_point(layer,p)
                    
        self.dxf_add( dxf_templates.r14_footer )

e = MyEffect()
e.affect()

