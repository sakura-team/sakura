// View
'use strict';
function View(){

    var thisView = this;

    L.TextBox = L.Control.extend({
        options: {
            position: 'topleft'
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
                L.DomUtil.create('div','message red',container);
            this._messageBox = messageBox;

            L.DomEvent
                .addListener(this._textBox, 'click', L.DomEvent.stop)
                .addListener(this._textBox, 'keyup', this._onKeyUp, this);
                
            L.DomEvent.disableClickPropagation(this._textBox);

            return this._container;
        },

        // get current text in the box
        getValue: function(){
            return this._textBox.value;
        },

        // reset Value of text box to default
        resetValue: function(){
            this._textBox.value = "";
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

    L.Button = L.Control.extend({
        options: {
            position: 'topleft'
        },

        initialize: function(options){
            this._config = {};
            L.Util.extend(this.options, options);
            this.setConfig(options);
        },

        setConfig: function(options){
            this._config = {
                sign: options.sign,
                titleButton: options.titleButton
            };
        },

        onAdd: function(map) {
            // container div in HTML
            var container = L.DomUtil.create('div','leaflet-control leaflet-bar'),
                link = L.DomUtil.create('a', '', container);
            this._container = container;
            this._link = link;

            // div attributs
            link.href = '#';
            link.title = this._config.titleButton;
            link.innerHTML =  this._config.sign;

            L.DomEvent.on(link, 'click', L.DomEvent.stop);
         
            return container;
        },

        getLink: function() {
            return this._link;
        }
    });

    L.ColorSelector = L.Control.extend({
        options: {
            position: 'topleft'
        },

        initialize: function(options){
            this._config = {};
            L.Util.extend(this.options, options);
            this.setConfig(options);
        },

        setConfig: function(options){
            this._config = {
                listColor: options.listColor,
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
    
            
            for(var i = 0; i < this._config.listColor.length ; i++){
                var option = document.createElement("option",'', container);
                option.text = this._config.listColor[i];
                option.style.background = this._config.listColor[i];
                option.style.color = this._config.listColor[i];
                select.add(option);
                L.DomEvent
                    .on(option, 'click', L.DomEvent.stop)
                    .on(option, 'click', function(){
                        select.style.background = select.options[select.selectedIndex].value;
                        select.style.color = select.options[select.selectedIndex].value;
                        });
                L.DomEvent.disableClickPropagation(option);
            }
            
            select.style.background = select.options[select.selectedIndex].value;
            select.style.color = select.options[select.selectedIndex].value;
            L.DomEvent
                .addListener(this._container, 'click', L.DomEvent.stop);
            
            L.DomEvent.disableClickPropagation(this._select);

            return select;
        },

        getSelect: function(){
            return this._select;
        },

        getColor: function() {
            return this._select.value;
        }
    });
    
    this.createColorSelector = function (map, listColor, title){
        var res = new L.ColorSelector({
            listColor: listColor,
            titleBox: title
        });
        res.addTo(map);

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

    this.createButton = function(map, sign, titleButton) {
        var res = new L.Button({sign: sign, titleButton: titleButton});

        res.addTo(map);

        return res;
    }

    this.nameBox = 
        thisView.createTextBox(map,"ResearchBox", "Current Research");

    /**
     *  Add button for creating a polygon
    */ 
    this.newPolygonButton =
        thisView.createButton(map,'▱','New polygon');
    // set up event for ROI creation
    L.DomEvent.on(this.newPolygonButton.getLink(), 'click', function () {
                      map.editTools.startPolygon(); 
            });
    var deleteShape = function (e) {
      if ((e.originalEvent.ctrlKey || e.originalEvent.metaKey) && this.editEnabled()){
        this.editor.deleteShapeAt(e.latlng);
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
        e.layer.bindTooltip("Polygon "+index).openTooltip();
        myController.addOverlays(e.layer, 'Polygon'+index);
        myController.actualize();
    });
        
    /**
     *  Add button for save current research
     */ 
    this.saveResearchButton =
        thisView.createButton(map,'↓','Save Research');
    L.DomEvent.on(this.saveResearchButton.getLink(), 'click', function() {
                        myController.addResearch();
                    });

    /**
    *  Add button for reset current research
    */ 
     this.resetResearchButton =
        thisView.createButton(map,'¤','Reset Research');
    L.DomEvent.on(this.resetResearchButton.getLink(), 'click', function(){
        myController.resetResearch();
    });

    /**
     *  Add background color selector 
     */ 
    var colors = ['Red', 'Orange', 'Yellow', 'Green', 'Cyan' , 'Blue' , 'Purple' ];
    this.backgroundColorSelector =
        thisView.createColorSelector(map,colors,'Background Color');
    L.DomEvent.on(this.backgroundColorSelector.getSelect(), 'change', function(){
        myController.actualize();
    });
    
    
    /**
     *  Add tweets color selector 
     */ 
    this.tweetsColorSelector =
        thisView.createColorSelector(map,colors,'Tweets Color');

    
    /**
     * Add layers control panel
     */
    this.layersPanel =
        L.control.layers(myModel.mapLayers.dict);
    this.layersPanel.addTo(map);
    myModel.mapLayers.getDefault().addTo(map);

    /**
     * Add overlays control panel
     */
    
    this.overlaysPanel =
        L.control.layers();
    this.overlaysPanel.addTo(map);
}

var myView = new View();
