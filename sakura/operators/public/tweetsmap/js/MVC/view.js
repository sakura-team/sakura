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
                // create options for obj
                V.setOptions(this, this.options);
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
            V.extend(this.options,options);
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

        noneDisplay: function(){
            this._container.style.display = 'none';
        },

        display: function(){
            this._container.style.display = 'inline';
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
            if(!this._messageBox){
                 // create message box in container in HTML
                this._messageBox =
                    V.create('div','message text-basic text-border');
                this._container.appendChild(this._messageBox);
            }
            this._messageBox.innerHTML = message;
            
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
            this._container.id = options.idDiv || '';
            this._container.style.overflow = options.scroll || 'visible'  ;
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
        	this._container.removeChild(child);
        }
    	
    	

    });


    
    V.Div = V.Element.extend({
        
        initialize: function(options){
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
        }

    });
    
    V.Selector = V.Element.extend({
    	initialize: function(options){
    		V.extend(this.options, options);
    		
    	},
    	
    	initSelector(){
    		this._rows = [];
    		this._selectorOptions();
    		var len = this.rowSource.length;
    		for(var i=0; i<len; i++){
    			// createRow is defined by child class of selector
    			this._addRow(this._createRow(this.rowSource[i]));
    		}
    	},
    	
    	_selectorOptions: function(){
    		var options = this.options;
    		// create shortcut for rowSource
    	    this.rowSource = options.rowSource || [];
    		
    	},
    	
    	// @function addRows(element HTMLElement?V.Class)
    	// add a Row to selector
    	_addRow: function(element){
    		this.addChild(element);
    		this._rows.push(element);
    	},
    	
    	_getIndex: function(DomEl){
    	    var i, len = this._rows.length;
    	    for(i = 0; i<len ; i++){
    	        if(this._rows[i].getContainer() == DomEl)
    	            return i;
    	    }
    	},
    	
    	// @function removeRows(index int)
    	// remove a Row by index in rows
    	removeRow: function(index){
    		// get Element to remove
    		var element = this._rows.splice(index, 1)[0];
    		// remove from container
    		this.rmChild(element);
    	},
    	
    	// empty the selector: 
    	removeAllRow: function(){
    		var len = this._rows.length;
    		for(var i=len-1; i>=0; i--){
    			this.removeRow(i);
    		}
    	},
       
        _getIndexById: function(name){
            var i, len = this._rows.length;
            console.log(len);
            for(i = 0; i < len; i++){
                if(this._rows[i].id == name) return i;
                console.log(this._rows[i].id);
            }
        }   	
    });
    
    V.MaplayersSelector = V.Selector.extend({
    	initialize: function(options){
			V.extend(this.options, options);
    		this.setContainer(V.create('div', 'mapLayersSelector'));
			this.initSelector();
    	},
		
		_createRow: function(layerName){
			var res = new V.Div({class: 'row-box'});
			var checkBox = new V.Div({class: 'roundedOne', parentElement: res});
			var child1 = V.create('input','', checkBox.getContainer());
			res.box = child1;
			child1.type = 'checkbox';
			child1.value = 'None';
			child1.name = 'check';
			child1.id = layerName;
			var child2 = V.create('label', '', checkBox.getContainer());
			child2.htmlFor = layerName;
			var child3 = V.create('p', '', res.getContainer());
			child3.innerHTML = layerName;

			child1.addEventListener('click', this._onClick.bind(this), false);
			return res;
			
		},

		check: function(index){
			var len = this._rows.length;
			for(var i =0; i<len; i++){
				this._rows[i].box.checked = (i==index);
			}
			this.currentCheckedBox = this._rows[index].box;
		},
		
		_onClick: function(e){
			var target = e.target || e.srcElement;  
			this.currentCheckedBox.checked = 
			   (this.currentCheckedBox == target);
			this.currentCheckedBox = target;
			myController.setBasemap(target.id);
		}

		
		
    }); 

    V.UserLayersSelector = V.Selector.extend({
        options: {
            rowSource: myModel.researches
        },
        
        initialize: function(options){
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
            this.initSelector();
        },
        
        _createRow: function(research){
            var row = new V.Div({
                class: 'row-researches-panel leaflet-bar'});
            var iconsBarre = new V.Div({class:  'iconsBarre', parentElement: row});
            row.plusIcon = new V.PlusIcon({checked:false, enabled: true, 
                                parentElement: row, idDiv: research.nameResearch});
            row.nameResearch = V.create('p','normal-text', row.getContainer());
            row.nameResearch.innerHTML = research.nameResearch;
            row.eyeIcon = new V.EyeIcon({checked: false, enabled: true, 
                                parentElement: iconsBarre});
            row.editionIcon = new V.EditionIcon({checked: true, enabled: true, 
                                parentElement: iconsBarre});
            row.trashIcon = new V.TrashIcon({checked: false, enabled: true, 
                                parentElement: iconsBarre, idDiv: research.nameResearch});
            row.exportationIcon = new V.ExportationIcon({cheked: true, 
                                enabled: false, parentElement: iconsBarre});
            row.trashIcon.getContainer().addEventListener('click',
                                this._deleteResearch.bind(this), false);
            row.id = research.nameResearch;
            
            return row;
        },
        
        addRow: function(research){
            var el = this._createRow(research);
            this._addRow(el);
        },
  
        
        _deleteResearch: function(e){
            console.log(e.currentTarget);
            var nameResearch = e.currentTarget.id;
            console.log(nameResearch);
            var i = this._getIndexById(nameResearch);
            console.log(i);
            this.removeRow(i);
            myController.removeResearch(i);
        }
    });
    
	
    V.TextBox = V.Element.extend({
        options: {
            class: 'text-box leaf-bar',
            hasMessage: true
        },

        initialize: function (options) {
            V.extend(this.options, options);
            
            this.setContainer(V.create('div'));
            this.textboxOptions();
            
            
            // create text box in container in HTML 
            var textBox = 
                V.create('input','',this._container);
            textBox.id = this._tbid;
            textBox.type = 'text';
            textBox.placeholder = this._textdefault;
            this._textBox = textBox;
            
            this._submitButton = new V.PlusIcon({iconChecked: 'fa fa-plus', 
                enabled: true, checked: true, parentElement: this._container});
            
            
            this._textBox.addEventListener('keyup', this._onKeypressed, false);
            
        },

        textboxOptions: function() {
            var options = this.options;
            console.log(options);
            this._tbid = options.tbid || '';
            this._textdefault = options.textdefault || '';
           
        },

        // get current text in the box
        getValue: function(){
            return this._textBox.value;
        },

        // reset Value of text box to default
        setValue: function(name){
            this._textBox.value = name;
        },
        
        disable: function() {
            this._submitButton.getContainer().removeEventListener('click', 
                                    this._onClick, false);
            this._submitButton.disable();
        },

        enable: function() {
            this._submitButton.getContainer().addEventListener('click', 
                                    this._onClick, false);
            this._submitButton.enable();
        },
        // update data when text box is changed
        _onClick: function(e){
            myController.actualize();
            myController.addResearch();
        },
        
        _onKeypressed: function(){
            myController.actualize();
        }


    });

   
    // this.nameBox = 
    //     thisView.createTextBox(map,"ResearchBox", "Current Research");

	// Notice: O
    V.Button = V.Element.extend({

        initialize: function(options){
            V.extend(this.options,options);
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
    
    V.Icon = V.Element.extend({
        initialize: function(options){
            V.extend(this.options, options);
        },
        
        initIcon: function(){
            this.setContainer(V.create('div', 'icon'));
            this._iconOptions();
            var className = (this.checked)?this.iconChecked:this.iconUnchecked;
            this._icon = V.create('i',className, this._container);
            (this.enabled)?this.enable():this.disable();
            
        },
        
        disable: function(){
            if(this.checked) this._onClick();
            this._container.style.backgroundColor = 'transparent';
            this.enabled = false;
            this._container.style.cursor = 'initial';
            this._container.style.boxShadow = '';
            V.DomUtil.removeClass(this._container, 'enabled');
            this._container.removeEventListener('click', 
                                               this._onClick.bind(this), false);
        },
        
        enable: function(){
            this._container.style.backgroundColor = 'white';
            V.DomUtil.addClass(this._container,'enabled');
            this.enabled = true;
            this._container.addEventListener('click', 
                                               this._onClick.bind(this), false);
            this._container.style.cursor = 'pointer';
            this._container.style.boxShadow 
                     ='inset 0px 1px 1px white, 0px 1px 3px rgba(0, 0, 0, 0.5)';
        }
        ,
        
        _iconOptions: function(){
            var options = this.options;
            
            this.iconUnchecked = options.iconUnchecked || 'fa fa-bath';
            this.iconChecked = options.iconChecked || 'fa fa-bath';
            this.checked = options.checked;
            this.index = options.index || -1;
            this.enabled = options.enabled;
        },
        
        _onClick: function(){
            this.checked = !this.checked;
            var className = (this.checked)?this.iconChecked:this.iconUnchecked;
            V.DomUtil.setClass(this._icon, className);
            this._eventHandle();
        }
    });
    
    V.PlusIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-plus',
            iconChecked: 'fa fa-minus'
        },
        initialize: function(options){

            V.extend(this.options, options);
            this.initIcon();
        },
        _eventHandle: function(){
            null
        }
    });
    
    V.EyeIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-eye-slash',
            iconChecked: 'fa fa-eye'
        },
        initialize: function(options){

            V.extend(this.options, options);
            this.initIcon();
            this.isEye = true;
        },
        _eventHandle: function(){
            null
        }
    });
    
    V.EditionIcon = V.Icon.extend({
        options: {
            iconChecked: 'fa fa-pencil',
            iconUnchecked: 'fa fa-pencil-square'
        },
        initialize: function(options){
            V.extend(this.options, options);
            this.initIcon();
        },
        _eventHandle: function(){
            null
        }
    });
    
    V.TrashIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-trash',
            iconChecked: 'fa fa-truck'
        },
        initialize: function(options){
            V.extend(this.options, options);
            this.initIcon();
        },
        _eventHandle: function(){
            null
        }
    });
    
    V.ExportationIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-cloud-download',
            iconChecked: 'fa fa-cloud-download'
        },
        initialize: function(options){
            V.extend(this.options, options);
            this.initIcon();
        },
        _eventHandle: function(){
            null
        }
    });
    

    V.ColorSelector = V.Element.extend({

        initialize: function(options){
            options = V.extend(this.options,options);
        
            // container div in HTML
            var container = this.setContainer(V.create('div'));

            var select = V.create('select','leaflet-bar', container);
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
        var index = myController.registerPoly(e.layer);
        var namePoly = myController.editableResearch.nameResearch + " " + index;
        e.layer.namePoly = namePoly;
        e.layer.bindTooltip(e.layer.namePoly).openTooltip();
        ////myController.addOverlays(e.layer, e.layer.namePoly);
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
    ////this.layersPanel =
    ////    L.control.layers(myModel.mapLayers.dict);
    ////this.layersPanel.addTo(map);
    myModel.mapLayers.dict['Plan'].addTo(map);
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
        res = L.DomUtil.create("div", 'champComposant leaflet-bar ', parent);
        

        return res;
    }
    
    /**
     * Edit box div 
     * Position: left
     * id = research
     * see research.css
     */ 
    var mapDiv = document.getElementById('map')
    this.editionDiv = new V.Div({parentElement: mapDiv, class: "leaflet-bar normal-text",
                            childClass: 'champComposant leaflet-bar', idDiv: 'research'});
    // hide varable
    this.editionDiv.hideState = true;
    this.editionDiv.stopEventOfLeaflet();

    // research name
    this.editionTitle = new V.Div({class: 'edition-title text-basic text-border', parentElement: mapDiv});
    this.editionTitle.getContainer().innerHTML = 'Name research';
    // hide div
    function hideResearch(){

        if(thisView.editionDiv.hideState == true){
            thisView.editionTitle.hide();
            thisView.editionDiv.hide();
            thisView.editionHide.setSign("►");
            thisView.editionHide.getContainer().style.left = '0px';
        }
        else {
            thisView.editionTitle.show();
            thisView.editionDiv.show();
            thisView.editionHide.setSign("◄");
            thisView.editionHide.getContainer().style.left = '25%';
        }   
            thisView.editionDiv.hideState = !thisView.editionDiv.hideState;
    }

    this.editionHide = new V.Button({sign: '◄', titleElement: 'Hide research', 
    				class: 'hideResearch', parentElement: mapDiv});
    L.DomEvent.on(this.editionHide.getLink(), 'click', hideResearch);

    //--------------- Fill Editiontools box --------------------
   

    
    var editBox = new V.Div({titleDiv: "Edition Tools", parentElement: this.editionDiv,
                            childClass: 'childOfEditTools',
                            titleDivClass: 'underChampComposant title text-border firstComposant'});

    var timeBox = new V.Div({titleDiv: "Time Interval", parentElement: this.editionDiv,
                            titleDivClass: 'underChampComposant title text-border firstComposant'});
    var colorBox = new V.Div({titleDiv: "Color Selections", parentElement: this.editionDiv,
                            titleDivClass: 'underChampComposant title text-border firstComposant'});

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
    /**
    *  Add button for reset current research
    */ 
    this.resetResearchButton = new V.Button({sign: '♺', titleElement: 'Reset Research',
                            parentElement: editBox});
  


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
            var container = V.create('div','timeSelector',parent);
            this._container = container;
            this._textDiv = V.create('div', '',container);
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
        
        var container = V.create('div','colorSelector',parent);
        
        var textDiv = V.create('div', 'normal-text',container);
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
    this.managementDiv = new V.Div({class: "leaflet-bar",
    								parentElement: mapDiv, childClass:' champComposant leaflet-bar',
    								idDiv: "management"});
    
    this.managementDiv.stopEventOfLeaflet();
    // hide varable
    				
    // hide varable
    this.managementDiv.hideState = false;

    function hideManangement(){

        if(thisView.managementDiv.hideState == true){
            thisView.managementDiv.hide();
            thisView.hideManagementButton.setTitle('Show management');
            thisView.hideManagementButton.setSign("◄");
            thisView.hideManagementButton.getContainer().style.right = '0px';
        }
        else {
            thisView.managementDiv.show();
            thisView.hideManagementButton.setTitle('Hide management');
            thisView.hideManagementButton.setSign("►"); 
            thisView.hideManagementButton.getContainer().style.right = '30%';  
            
        }    
        thisView.managementDiv.hideState = !thisView.managementDiv.hideState;

    }
    this.hideManagementButton = new V.Button({sign: '◄', titleElement: 'Hide management', 
    				class: 'hideManagement', parentElement: mapDiv});
    			
    L.DomEvent.on(this.hideManagementButton.getContainer(), 'click', hideManangement);
    

    // research name
    //this.editionTitle = L.DomUtil.create('div','firstComposant text-basic text-border',this.editionDiv);
    //this.editionTitle.innerHTML = 'Name research';

   
    this.baseMapsBox =  new V.Div({titleDiv: "Base Maps", parentElement: this.managementDiv,
                            titleDivClass: 'underChampComposant title text-border firstComposant'});
    this.userlayersBox = new V.Div({titleDiv: "User Layer", parentElement: this.managementDiv,
                            titleDivClass: 'underChampComposant title text-border firstComposant'});
	
    //----------------------Fill basemapsBox----------------------------------------/
	this.maplayersSelector = new V.MaplayersSelector({parentElement: this.baseMapsBox, class: 'normal-text',
							rowSource: Object.keys(myModel.mapLayers.dict)});
	
    //----------------------Fill userlayersBox-------------------------------------/
    this.nameBox = new V.TextBox({tbid : 'ResearchBox', textdefault: 'Name'});
    this.userlayersBox.addChild(this.nameBox);
    this.researchesPanel = //new V.Div({parentElement: this.userlayersBox, class: 'researches-panel'});
                 new V.UserLayersSelector({parentElement: this.userlayersBox, 
                            class: 'researches-panel'});
    
}



//---------------------------------------View Singleton-----------------------------------------------/
var myView = new View();

