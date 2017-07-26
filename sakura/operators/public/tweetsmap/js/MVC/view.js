// View
'use strict';
function View(){

    var thisView = this;

    //----------------------------------------Classes-------------------------------------------
    /**
     * Each class below represents a entiti on GUI 
     */

    var V = {};

    V.Util = {
        extend: function(dst){
            var i, j, len, src;

            for(i = 1, len = arguments.length; i < len; i++){
                src = arguments[i];
                for(j in src){
                    dst[j] = src[j];
                }
            }

            return dst;
        },

        // @function setOptions(obj: Object, options: Object): Object
	    // Merges the given properties to the `options` of the `obj` object, returning the resulting options. See `Class options`. Has an `L.setOptions` shortcut.
	    setOptions: function (obj, options) {
		    if (!obj.hasOwnProperty('options')) {
			    obj.options = obj.options ? Object.create(obj.options) : {};
		    }
		    for (var i in options) {
			    obj.options[i] = options[i];
		    }
		    return obj.options;
        }
        
    };

    V.DomUtil = L.DomUtil;

    V.create = V.DomUtil.create;
    V.addClass = V.DomUtil.addClass;
    V.toFront = V.DomUtil.toFront;

    // shortcuts for most used utility functions
    V.extend = V.Util.extend;
    V.setOptions = V.Util.setOptions;

    V.Class = function(){};

    V.Class.extend = function(props){

        var NewClass = function() {

            // call the constructor
            if(this.initialize){
                this.initialize.apply(this, arguments);
            }
        };
        
        var parentProto = NewClass.__super__ = this.prototype;

        var proto = Object.create(parentProto);
        proto.constructor = NewClass;

        NewClass.prototype = proto;

        for(var i in this) {
            if(this.hasOwnProperty(i) && i!== 'prototype'){
                NewClass[i] = this[i];
            }
        }

        if(proto.options) {
            props.options = V.Util.extend(L.Util.create(proto.options), props.options);
        }

        V.extend(proto, props);

        return NewClass;

    }

        // An element HTML
    V.Element = V.Class.extend({

        options: {

            // Contain a text div for displaying a message
            // for example error message 
            hasMessage: false
        },

        initialize: function(options) {
            options = V.setOptions(this,options);

            
        },

        // @function show
        // set Element visble
        show: function(){
            this._container.style.visibility = 'visible';
        },

        // @function hide
        // set Element invisible
        hide: function(){
            this._container.style.visibility = 'hidden';
        },

        nonedisplay: function(){
            this._container.display = 'none';
        },

        display: function(){
            this._container.display = 'inline';
        },

        setTitle: function(title) {
            if(title)
                this._container.title = title;
            else if(this.options.titleElement)
                this._container.title = this.options.titleElement;
        },
        
        // @function setMessage(message: String)
        // set messgage to message box
        // example: notify a duplication name
        setMessage: function(message){
            if(this.options.hasMessage && !this._message){
                 // create message box in container in HTML
                var messageBox =
                    V.create('div','message text-basic text-border');
                this._messageBox = messageBox;
                this._container.appendChild(this._messageBox);
                this._messageBox.innerHTML = message;
            }
            
        },

        addOn: function(parent) {
            parent.appendChild(this._container);
        },

        addClass: function(className) {
            V.addClass(this._container, className);
        },

        getContainer: function() {
            return this._container;
        },
        
        // @function setContainer(element: HTMLElement)
        setContainer: function(element) {
        	this._container = element;
        	this._classOptions();
        	
        	return this._container;
        },
        
        // @function _classOptions() 
        // Check and add attributs for container 
        _classOptions: function(){
        	var options = this.options;
        	if(this.options.titleElement)
                this._container.title = this.options.titleElement;
        	if(options.class)
                V.addClass(this._container,options.class);
            if(options.idDiv)
                this._container.id = options.idDiv;
            if(options.scrollable)
                this._container.style.overflow = 'auto';
            if(options.titleDiv){
                var firtChild = V.create("div", options.titleDivClass, this._container);
                firtChild.innerHTML = options.titleDiv;
            }
            if(options.parentElement){
                if(options.parentElement.addChild)
                    options.parentElement.addChild(this._container);
                else 
                    options.parentElement.appendChild(this._container);
            }
            if(options.eventClick){
            	L.DomEvent.on(this.getContainer(), 'click', function(){
            	options.eventClick.functionName.call(options.eventClick.className)});
            }
        },
        
        stopEventOfLeaflet: function() {
        	var div = this._container;
        	if (!L.Browser.touch) {
        	    L.DomEvent.disableClickPropagation(div);
        	    L.DomEvent.on(div, 'mousewheel', L.DomEvent.stopPropagation);
        	} else {
            	L.DomEvent.on(div, 'click', L.DomEvent.stopPropagation);
        	}
    	},
    	
        // @function addChild(child HTMLelement?V.Class) 
        // Add child to container  
        addChild: function(child){
            if(child._container)
                child = child._container;
            this._container.appendChild(child);
            if(this.options.childClass){
                V.addClass(child,this.options.childClass);
            }

            return this;
        },
        
        // @function rmChild(child HTMLelement?V.Class) 
        // Remove a child from container
        rmChild: function(child){
        	if(child._container)
        		child = child._container;
        	this._container.rmChild(child);
        }
    	
    	

    });


    
    V.Div = V.Element.extend({
        
        initialize: function(options){
            V.setOptions(this, options);
            this.setContainer(V.create('div'));
        }

    });
    
    V.Selector = V.Element.extend({
    	initialize: function(options){
    		V.setOptions(this, options);
    		
    	},
    	
    	initSelector(){
    		this._rows = [];
    		this._selectorOptions();
    		var len = this.rowSource.length;
    		for(var i; i<len; i++){
    			// createRow is defined by child class of selector
    			this.addRow(this.createRow(this.rowSource[i]));
    		}
    	},
    	
    	_selectorOptions: function(){
    		var options = this.options;
    		if(options.rowSource){
    			// create shortcut for rowSource
    			this.rowSource = options.rowSource;
    		}
    	},
    	
    	// @function addRows(element HTMLElement?V.Class)
    	// add a Row to selector
    	addRow: function(element){
    		this.getContainer.addChild(element);
    		this._rows.push(element);
    	},
    	
    	// @function removeRows(index int)
    	// remove a Row by index in rows
    	removeRow: function(index){
    		// get Element to remove
    		var element = this._rows.slice(index, 1)[0];
    		// remove from container
    		this.rmChild(element);
    	},
    	
    	// empty the selector: 
    	removeAllRow: function(){
    		var len = this._rows.length;
    		for(var i=len-1; i>=0; i--){
    			this.removeRow(i);
    		}
    	}
    	
    });
    
    V.MaplayersSelector = V.Selector.extend({
    	initialize: function(){
    		this.setContainer(V.create('div'));
    	}
    }); 
    
    L.TextBox = L.Control.extend({
        options: {
            position: 'topright'
        },

        initialize: function (options) {
            this._config = {};
            L.Util.extend(this.options, options);
            this.setConfig(options);
        },

        setConfig: function(options) {
            this._config = {
                'tbid': options.tbid || '',
                'textdefault': options.textdefault || '',
            };
        },

        onAdd: function(map) {
            // create div container in HTML
            var container = 
                L.DomUtil.create('div', 'leaflet-control leaf-bar');
            this._container = container;

            // create text box in container in HTML 
            var textBox = 
                L.DomUtil.create('input','',container);
            textBox.id = this._config.tbid;
            textBox.type = 'text';
            textBox.placeholder = this._config.textdefault;
            this._textBox = textBox;

            // create message box in container in HTML
            var messageBox =
                L.DomUtil.create('div','message text-basic text-border',container);
            this._messageBox = messageBox;

            L.DomEvent
                .addListener(this._textBox, 'keyup', this._onKeyUp, this);
                
            L.DomEvent.disableClickPropagation(this._textBox);

            return this._container;
        },

        // get current text in the box
        getValue: function(){
            return this._textBox.value;
        },

        // reset Value of text box to default
        setValue: function(name){
            this._textBox.value = name;
        }
        ,

        setMessage: function(message){
            this._messageBox.innerHTML = message;
        },

        // update data when text box is changed
        _onKeyUp: function(e){
            myController.actualize();
        }


    });


	// Notice: O
    V.Button = V.Element.extend({

        initialize: function(options){
            options = V.setOptions(this,options);

            var container = this.setContainer(V.create('div', 'leaflet-bar')),
                link = V.create('a', '', container);
            this._container = container;
            this.setTitle();
            this._link = link;

            // div attributs
            link.href = '#';
            link.innerHTML =  this.options.sign;

            return container;
        },

        getLink: function() {
            return this._link;
        },

        setDisabled: function(bool){
            if(bool){
                //L.DomUtil.removeClass(this._container, 'leaflet-control');
                L.DomUtil.removeClass(this._container, 'leaflet-bar');
                this._container.style.display = 'none';
            }
            else{
                //L.DomUtil.addClass(this._container, 'leaflet-control');
                L.DomUtil.addClass(this._container, 'leaflet-bar');
                this._container.style.display = 'inline';
            }
        },
        invisible: function(bool) {
            if(bool) this._container.style.visibility = 'hidden';
            else this._container.style.visibility = 'visible';
        },

        setSign: function(sign) {
            this._link.innerHTML = sign;
        }
    });

    V.ColorSelector = V.Element.extend({

        initialize: function(options){
            options = V.setOptions(this,options);
        
            // container div in HTML
            var container = this.setContainer(V.create('div'));

            var select = V.create('select','leaflet-control leaflet-bar', container);
            this._select = select;
    
            
            for(var i = 0; i < this.options.listColor.length ; i++){
                var option = V.create("option",'', container);
                option.text = this.options.listColor[i];
                option.style.background = this.options.listColor[i];
                option.style.color = this.options.listColor[i];
                select.add(option);
                L.DomEvent
                    .on(option, 'click', function(){
                        select.style.background = select.options[select.selectedIndex].value;
                        select.style.color = select.options[select.selectedIndex].value;
                        });
                L.DomEvent.disableClickPropagation(option);
            }
            
            select.style.background = select.options[select.selectedIndex].value;
            select.style.color = select.options[select.selectedIndex].value;
            

            return select;
        },

        getSelect: function(){
            return this._select;
        },

        getColor: function() {
            return this._select.value;
        },

        setColor: function(color) {
            this._select.style.background = color;
            this._select.style.color = color;
            this._select.value = color;
        },

    });

    L.SelectBox = L.Control.extend({
        options: {
            position: 'topright'
        },

        initialize: function(options){
            this._config = {};
            L.Util.extend(this.options, options);
            this.setConfig(options);
        },

        setConfig: function(options){
            this._config = {
                listOptions: options.listOptions,
                titleBox: options.titleBox
            };
        },

        onAdd: function(map) {
            // container div in HTML
            var container = L.DomUtil.create('div');
            this._container = container;

            var select = L.DomUtil.create('select','leaflet-control leaflet-bar', container);
            this._select = select;
            select.title = this._config.titleBox;
            for(var i = 0; i < this._config.listOptions.length ; i++){
                this.addOption(this._config.listOptions[i]);
            }
            
            L.DomEvent
                .addListener(this._container, 'click', L.DomEvent.stop);
            
            L.DomEvent.disableClickPropagation(this._select);

            return select;
        },

        getSelect: function(){
            return this._select;
        },

        getValue: function() {
            return this._select.value;
        },

        addOption: function(text) {
            var option = document.createElement("option",'',this._container);
            option.text = text;
            this._select.add(option);
            L.DomEvent
                    .on(option, 'click', L.DomEvent.stop)
            L.DomEvent.disableClickPropagation(option);
        },

        removeOption:function(index) {
            this._select.remove(index);
        },

        removeAllOptions:function() {
            for(var i = this._select.options.length-1;i>=0;i--)
            {
                this._select.remove(i);
            }
        },

        setTextOfOption(index, text) {
            this._select.options[index].text = text;
            if(index == this._select.selectedIndex){
                this._select.text = text;
            }
        },

        setSelectedOption(index) {
            this._select.selectedIndex = index;
        }
    });

    L.CheckBoxList = L.Control.extend({
        options: {
            position: 'topright'
        },

        initialize: function(options){
            this._config = {};
            L.Util.extend(this.options, options);
            this.setConfig(options);
        },

        setConfig: function(options){
            this._config = {
                listBoxes: options.listBoxes,
                titleBox: options.titleBox,
            };
        },

        onAdd: function(map) {
            // container div in HTML
            var container = document.createElement('div')
            container.className = 'leaflet-control leaflet-bar';
            this._container = container;
            container.title = this._config.titleBox;

            for(var i = 0; i < this._config.listBoxes.length ; i++){
                this.addCheckBox(this._config.listBoxes[i]);
            }
            
            return container;
        },

        addCheckBox: function(text) {
            // line = checkbox + lineText
            var line = document.createElement("div");
            this._container.appendChild(line);
            // for line break
            line.style.float = 'left';
            line.style.fontSize = "14px";

            var checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.style.float = 'left';
            checkbox.className = 'leaflet-control-layers-selector';
            line.appendChild(checkbox);

            var lineText = L.DomUtil.create('div', '',line);
            lineText.style.float = 'left';            
            lineText.innerHTML = text;
            lineText.className = 'text-basic text-border';
            var thisNow = this;
            
            L.DomEvent.on(checkbox, "click", function(){
                var lineIndex = Array.prototype.indexOf.call(thisNow._container.children, line);
                if(checkbox.checked){
                    myController.displayResearch(lineIndex);
                } else {
                    myController.hideResearch(lineIndex);                    
                }
                myController.actualize();
            });
                                
        },

        removeCheckBox: function(index) {
            var line = this._container.children[index];
            this._container.removeChild(line);
        },

        removeAllCheckboxes: function() {
            for(var i = this._container.children.length-1;i>=0;i--)
            {
                this.removeCheckBox(i);
            }
        },

        setTextOfCheckBox: function(index, text) {
            this._container.children[index].children[1].innerHTML = text + "<br>";
        },

        // check the box
        setChecked: function(index, checked) {
            this._container.children[index].children[0].checked = checked;
        },

        // set box to uncheckable (bool = false)/ checkable (bool = true)
        setCheckable: function(index, disabled) {     
            this._container.children[index].children[0].disabled = disabled;
        },

        getChecked: function(index) {
            return this._container.children[index].children[0].checked;
        }

    });

    L.MessageBox = L.Control.extend({
        options: {
            position: "bottomright"
        },

        onAdd: function(map) {
            this._container= L.DomUtil.create('div');
            return this._container;
        },

        setClass: function(className) {
            this._container.className = className;
            this._container.style.float = 'right';  
            this._container.style.margin = '0px 6px 6px 0px';
        },

        update: function(text) {
            this._container.innerHTML = text;
        },

        hide: function(){
            this._container.style.display = 'none';
        },
        show: function(){
            this._container.style.display = 'inline';
        }
    });


    //-----------------------------------------Creater------------------------------------------------

    /**
     * These functions are intended for creating the instances of the classes aboves
     * @return Entite on GUI
     */
    this.createMessageBox = function(map) {
        var res = new L.MessageBox;
        res.addTo(map);

        return res;
    }


    this.createSelector = function(map, list, title){
        var res  = new L.SelectBox({
            listOptions: list,
            titleBox: title
        });
        res.addTo(map);

        return res;
    }
    
    this.createCheckBoxList = function(map, list, title){
        var res  = new L.CheckBoxList({
            listBoxes: list,
            titleBox: title
        });
        res.addTo(map);

        return res;
    }


    this.createColorSelector = function (map, listColor, title){
        var res = new V.ColorSelector({
            listColor: listColor,
            titleBox: title
        });

        return res;
    };

    // add Box into Map
    this.createTextBox = function(map, tbid, textdefault) {
        // create box
        var res = new L.TextBox({
            tbid: tbid,
            textdefault: textdefault
        });
        // Display Box on Map
        res.addTo(map);

        return res;
    };

    this.createButton = function(sign, titleButton) {
        var res = new V.Button({sign: sign, titleElement: titleButton});

        return res;
    }

    //--------------------------------------Instances----------------------------------------------
    //---------------------------------------TOP LEFT----------------------------------------------
    // this.nameBox = 
    //     thisView.createTextBox(map,"ResearchBox", "Current Research");

    
    var deleteShape = function (e) {
      if ((e.originalEvent.ctrlKey || e.originalEvent.metaKey) && this.editEnabled()){
        var poly = this.editor.deleteShapeAt(e.latlng);
        //var poly = this.editor.deleteShapeAt(e.latlng);
        myController.deletePolygons(poly);
      }
    };
    map.on('layeradd', function (e) {
        if (e.layer instanceof L.Path) e.layer.on('click', L.DomEvent.stop).on('click', deleteShape, e.layer);
        if (e.layer instanceof L.Path) e.layer.on('dblclick', L.DomEvent.stop).on('dblclick', e.layer.toggleEdit);
    });

    // when finish drawing
    map.on('editable:drawing:end', function (e) {
        // save Poly
        var index = myController.registrerPoly(e.layer);
        var namePoly = myModel.currentResearch.nameResearch + " " + index;
        e.layer.namePoly = namePoly;
        e.layer.bindTooltip(e.layer.namePoly).openTooltip();
        myController.addOverlays(e.layer, e.layer.namePoly);
        myController.actualize();
        myController.updateMarkers();
    });

    // // when edit 
    // map.on('editable:vertex:dragend', function (e) {
    //     myController.updateMarkers();
    // });
    // map.on('editable:dragend', function (e) {
    //     myController.updateMarkers();
    // });    
    
    // /**
    //  *  Add button for save current research
    //  */ 
    // this.saveResearchButton =
    //     thisView.createButton(map,'↓ ','Save Research');
    // L.DomEvent.on(this.saveResearchButton.getLink(), 'click', function() {
    //                     myController.addResearch();
    //                 });

    // /**
    // *  Add button for reset current research
    // */ 
    // this.resetResearchButton =
    //     thisView.createButton(map,'♺','Reset Research');
    // L.DomEvent.on(this.resetResearchButton.getLink(), 'click', function(){
    //     myController.resetResearch();
    // });

    // /**
    //  *  Add button for remove current research
    //  */
    // this.removeResearchButton =
    //     thisView.createButton(map,'❎','Delete Research');
    // L.DomEvent.on(this.removeResearchButton.getLink(), 'click', function(){
    //     myController.removeResearch();
    // });

    // /**
    //  *  Add button for remove current research
    //  */
    // this.removeAllResearchButton =
    //     thisView.createButton(map,'❌','Delete All Researchs');
    // L.DomEvent.on(this.removeAllResearchButton.getLink(), 'click', function(){
    //     myController.removeAllResearch();
    // });

    // /**
    //  *  Add background color selector 
    //  */ 
    // var colors = ['Olive','Red', 'Orange', 'Yellow', 'Green', 'Cyan' , 'Blue' , 'Purple' ];
    // this.backgroundColorSelector =
    //     thisView.createColorSelector(map,colors,'Background Color');
    // L.DomEvent.on(this.backgroundColorSelector.getSelect(), 'change', function(){
    //     myController.actualize();
    // });
    
    
    // /**
    //  *  Add tweets color selector 
    //  */ 
    // this.tweetsColorSelector =
    //     thisView.createColorSelector(map,colors,'Tweets Color');

    //----------------------------------TOP RIGHT------------------------------------///
    
    // /**
    //  * Add recherche selectable checkbox list
    //  */
    
    // this.researchCheckBoxList =
    //     this.createCheckBoxList(map, [], 'Research CheckBox List');
    
    // /**
    //  * Add recherche select box
    //  */
    
    // this.researchSelector =
    //     this.createSelector(map, [], 'Research List');
    // L.DomEvent.on(this.researchSelector.getSelect(), 'change', function(){
    //      myController.selectResearch();
    // })
   
    /**
     * Add layers control panel
     */
    this.layersPanel =
        L.control.layers(myModel.mapLayers.dict);
    this.layersPanel.addTo(map);
    myModel.mapLayers.getDefault().addTo(map);
    // L.DomEvent.on(this.layersPanel.getContainer(), 'click', function(){
    //     myController.updateMarkers();
    // });
    // /**
    //  * Add overlays control panel
    //  */
    
    // this.overlaysPanel =
    //     L.control.layers();
    // this.overlaysPanel.addTo(map);
    
    // //---------------------------------Botton right-----------------------------
   

    // this.pointNumber = this.createMessageBox(map);
    // this.pointNumber.setClass("text-basic text-border");
    // this.pointNumber.update(" Data loading...")

    
    /**
     *  LayerGroup contain all ROIs displayed on Map 
     *  including polygons:
     *  + Polygons of research
     *  + ROI admin (not implemented)
     */
    this.rois =
        new L.LayerGroup;
    this.rois.addTo(map);

    this.displayedMarkers =
        new L.LayerGroup;
    this.displayedMarkers.addTo(map);

    //---------------------------------------------Button Organisation------------------------------------------//
    /**
     * @function stopEventOfLeaflet stop all map events
     * @param div div on which we want to stop all map events
     */
    /**
    this.stopEventOfLeaflet = function(div) {
         if (!L.Browser.touch) {
            L.DomEvent.disableClickPropagation(div);
            L.DomEvent.on(div, 'mousewheel', L.DomEvent.stopPropagation);
        } else {
            L.DomEvent.on(div, 'click', L.DomEvent.stopPropagation);
        }
    }*/
    
    /**
     * ChildBox div
     * under-div of Edit box or Research div
     * @param name name of box Ex Time Interval
     * @param parent the parent element 
     * @param bool true if this is the last child 
     * 
     */
    this.createChildBox = function(name, parent, bool) {
        var res;
        res = L.DomUtil.create("div", 'champComposant leaflet-control leaflet-bar ', parent);
        

        return res;
    }
    
    /**
     * Edit box div 
     * Position: left
     * id = research
     * see research.css
     */ 
    var mapDiv = document.getElementById('map')
    this.editionDiv = new V.Div({parentElement: mapDiv, class: "leaflet-bar title text-border",
                            childClass: 'champComposant leaflet-control leaflet-bar', idDiv: 'research'});
    // hide varable
    this.editionDiv.hideState = false;
    this.editionDiv.stopEventOfLeaflet();

    // research name
    this.editionTitle = new V.Div({class: 'edition-title text-basic text-border', parentElement: mapDiv});
    this.editionTitle.getContainer().innerHTML = 'Name research';
    // hide div
    function hideResearch(){

        if(thisView.editionDiv.hideState == true){
            thisView.editionTitle.hide();
            thisView.editionDiv.hide();
            thisView.hideButton.setSign("►");
            thisView.hideButton.getContainer().style.left = '0px';
        }
        else {
            thisView.editionTitle.show();
            thisView.editionDiv.show();
            thisView.hideButton.setSign("◄");
            thisView.hideButton.getContainer().style.left = '25%';
        }    
            thisView.editionDiv.hideState = !thisView.editionDiv.hideState;
    }

    this.hideButton = new V.Button({sign: '►', titleElement: 'Hide research', 
    				class: 'hideResearch', parentElement: mapDiv});
    L.DomEvent.on(this.hideButton.getLink(), 'click', hideResearch);

    //--------------- Fill Editiontools box --------------------
   

    /**
    *  Add button for reset current research
    */ 
    this.resetResearchButton = new V.Button({sign: '♺', titleElement: 'Reset Research'});
    L.DomEvent.on(this.resetResearchButton.getLink(), 'click', function(){
        myController.resetResearch();
    });

    var editBox = new V.Div({titleDiv: "Edition Tools", parentElement: this.editionDiv,
                            childClass: 'childOfEditTools',
                            titleDivClass: 'underChampComposant title firstComposant'});

    var timeBox = new V.Div({titleDiv: "Time Interval", parentElement: this.editionDiv,
                            titleDivClass: 'underChampComposant title firstComposant'});
    var colorBox = new V.Div({titleDiv: "Color Selections", parentElement: this.editionDiv,
                            titleDivClass: 'underChampComposant title firstComposant'});

    // this.newPolygonButton.addOn(editBox);
    // this.newPolygonButton.addClass("childOfEditTools");
    // this.newRectangleButton.addOn(editBox);
    // this.newRectangleButton.addClass("childOfEditTools");
    // this.newCircleButton.addOn(editBox);
    // this.newCircleButton.addClass("childOfEditTools");
    // this.resetResearchButton.addOn(editBox);
    // this.resetResearchButton.addClass("childOfEditTools");
    /**editBox.addChild(this.newPolygonButton)
            .addChild(this.newRectangleButton)
            .addChild(this.newCircleButton)
            .addChild(this.resetResearchButton);*/
	 /**
     *  Add button for creating a zone
    */ 
    this.newPolygonButton = new V.Button({sign: '▱', titleElement: 'New polygon',
    						parentElement: editBox, 
    						eventClick: {className: map.editTools, functionName: 
    							map.editTools.startPolygon}});
    
    this.newRectangleButton = new V.Button({sign: '▭', titleElement: 'New rectangle',
    						parentElement: editBox,
    						eventClick: {className: map.editTools, functionName: 
    							map.editTools.startRectangle}});
   
    this.newCircleButton = new V.Button({sign: '◯', titleElement: 'New Circle',
    						parentElement: editBox,
    						eventClick: {className: map.editTools, functionName: 
    							map.editTools.startCircle}});
    


    // for(var i=1; i < editBox.children.length;i++){
    //     editBox.children[i].style.top = -(i-2)*20 + 'px' ;
    //     editBox.children[i].style.left = (i*30)+'px';
    // }
    
    //---------------Fill TimeInterval box-------------------

    V.timeSelector = V.Element.extend({
        options: {
            hasMessage: true
        },


        initialize: function(text, date, month, year, parent){
            var container = L.DomUtil.create('div','timeSelector',parent);
            this._container = container;
            this._textDiv = L.DomUtil.create('div', 'text-border',container);
            this._textDiv.innerHTML = text ;
            this._dateDiv = L.DomUtil.create('select', '',container);
            for(var i=1;i<31; i++){
                var option = L.DomUtil.create('option', 'timeOption', this._dateDiv);
                option.text = i;
                
            }

            this._dateDiv.defaultValue = date;
            this._dateDiv.text = date;
            this._dateDiv.value = date;
            
            this._monthDiv = L.DomUtil.create('select', '',container);
            for(var i=0;i<this.monthsShort.length; i++){
                var option = L.DomUtil.create('option', 'timeOption', this._monthDiv);
                option.text = this.monthsShort[i];
            }
            this._monthDiv.defaultValue = month;
            this._monthDiv.value = month;

            this._yearDiv = L.DomUtil.create('select', '',container);
            for(var i = 2007; i<= 2017; i++){
                var option = L.DomUtil.create('option', 'timeOption', this._yearDiv);
                option.text = i;
            }
            this._yearDiv.defaultValue = year;
            this._yearDiv.value = year;



            return this;
        },

        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],

        getDate: function(){
            return this._dateDiv.value;
        }

    });

    this.startTimetDiv = new V.timeSelector("Start", 23, 'Dec', 2017);
    this.startTimetDiv.setMessage("Hello, Wolrd!");
    this.endTimetDiv = new V.timeSelector("End", 23, 'Dec', 2017);

    timeBox.addChild(this.startTimetDiv).addChild(this.endTimetDiv);

    //-------------------Fill Color Selector--------------------------------//
    /**
     *  Add background color selector 
     */ 
    var colors = ['Olive','Red', 'Orange', 'Yellow', 'Green', 'Cyan' , 'Blue' , 'Purple' ];
    this.backgroundColorSelector = new V.ColorSelector({
            listColor: colors,
            titleElement: 'Background Color'
    	});
    L.DomEvent.on(this.backgroundColorSelector.getSelect(), 'change', function(){
        myController.actualize();
    });
    this.boundColorSelector = new V.ColorSelector({
    		listColor: colors,
    		titleElement: 'Bound Color'		
    	});
    
    /**
     *  Add tweets color selector 
     */ 
    this.tweetsColorSelector = new V.ColorSelector({
    		listColor: colors,
    		titleElement: 'Tweets Color'
    	});

    function addColorSelector(text, child, parent){
        
        var container = L.DomUtil.create('div','colorSelector',parent);
        
        var textDiv = L.DomUtil.create('div', 'text-border',container);
        textDiv.innerHTML = text ;
        var colorSelector = child;
        container.appendChild(colorSelector);

        return container;
    }

    addColorSelector('Bound', thisView.boundColorSelector.getContainer(), colorBox.getContainer());
    addColorSelector('Background', thisView.backgroundColorSelector.getContainer() ,colorBox.getContainer());
    addColorSelector('Tweets', thisView.tweetsColorSelector.getContainer() ,colorBox.getContainer());

    /**
     * Recherche Management box div 
     * Position: right
     * id = management
     * see management.css
     */ 
    this.managementDiv = new V.Div({class: "leaflet-control leaflet-bar title text-border",
    								parentElement: mapDiv, childClass:'champComposant leaflet-control leaflet-bar',
    								idDiv: "management"});
    
    // hide varable
    				
    // hide varable
    this.managementDiv.hideState = false;

    function hideManangement(){

        if(thisView.managementDiv.hideState == true){
            thisView.managementDiv.hide();
            thisView.hideManangementButton.setTitle('Show management');
            thisView.hideManagementButton.setSign("◄");
        }
        else {
            thisView.managementDiv.show();
            thisView.hideManagementButton.setTitle('Hide management');
            thisView.hideManagementButton.setSign("►"); 
        }    
        thisView.managementDiv.hideState = !thisView.managementDiv.hideState;

    }
    this.hideManagementButton = new V.Button({sign: '►', titleElement: 'Hide management', 
    				class: 'hideManagement', parentElement: mapDiv});
    			
    L.DomEvent.on(this.hideManagementButton.getContainer(), 'click', hideManangement);
    

    // research name
    //this.editionTitle = L.DomUtil.create('div','firstComposant text-basic text-border',this.editionDiv);
    //this.editionTitle.innerHTML = 'Name research';

   
    this.createChildBox 
    					=  new V.Div({titleDiv: "Base Maps", parentElement: this.managementDiv,
                            titleDivClass: 'underChampComposant title firstComposant'});
    this.userlayersBox = 
    					new V.Div({titleDiv: "User Layer", parentElement: this.managementDiv,
                            titleDivClass: 'underChampComposant title firstComposant'});
    //----------------------Fill basemapsBox----------------------------------------/

    //----------------------Fill userlayersBox-------------------------------------/
}



//---------------------------------------View Singleton-----------------------------------------------/
var myView = new View();

