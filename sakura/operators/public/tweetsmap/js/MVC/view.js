// View
'use strict';
function View() {

    var thisView = this;

    //----------------------------------------Classes-------------------------------------------
    /**
     * Each class below represents a entiti on GUI 
     */

    var V = {};

    V.Util = {
        extend: function (dst) {
            var i, j, len, src;
            for (i = 1, len = arguments.length; i < len; i++) {
                src = arguments[i];
                for (j in src) {
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
        },

        convertColor: function (colorCode, opacity) {
            return colorCode.substr(0, colorCode.length - 5) + opacity + ')';
        },

        reverseArray: function (array) {
            var i, len = array.length;
            var res = [];
            for (i = 0; i < len; i++) {
                var res_el = [];
                res_el.push(parseFloat(array[i][1]) * 100);
                res_el.push(parseFloat(array[i][0]) * 100);
                res.push(res_el);
            }
            var nbSommet = len, tolerance = 0.1
            while (nbSommet >= 35) {
                res = simplify(res, tolerance, false);
                tolerance += 0.1;
                nbSommet = res.length;
            }
            var res1 = [], len = res.length;
            for (i = 0; i < len; i++) {
                var res_el = [];
                res_el.push(parseFloat(res[i][0]) / 100.0);
                res_el.push(parseFloat(res[i][1]) / 100.0);
                res1.push(res_el);
            }
            return res1;
        },


        convertMarkerColor: function (colorCode) {
            var i, colors = ['olivedrab', 'red', 'orange', 'pink', 'green', 'lightskyblue', 'blue', 'purple'];
            var len = colors.length, lenCode = colorCode.length;
            for (i = 0; i < len; i++) {
                if (colorCode.substr(0, lenCode - 5) == thisView.colors[i].substr(0, lenCode - 5)) {
                    switch (colors[i]) {
                        case "olivedrab": return "darkgreen";
                        case "lightskyblue": return "lightblue";
                        case "blue": return "darkblue";
                        default: return colors[i];
                    }
                }
            }
        }

    };

    V.DomUtil = L.DomUtil;

    V.create = V.DomUtil.create;
    V.addClass = V.DomUtil.addClass;
    V.toFront = V.DomUtil.toFront;

    // shortcuts for most used utility functions
    V.extend = V.Util.extend;
    V.setOptions = V.Util.setOptions;

    V.Class = function () { };

    V.Class.extend = function (props) {

        var NewClass = function () {

            // call the constructor
            if (this.initialize) {
                // create options for obj
                V.setOptions(this, this.options);
                this.initialize.apply(this, arguments);
            }
        };

        var parentProto = NewClass.__super__ = this.prototype;

        var proto = Object.create(parentProto);
        proto.constructor = NewClass;

        NewClass.prototype = proto;

        for (var i in this) {
            if (this.hasOwnProperty(i) && i !== 'prototype') {
                NewClass[i] = this[i];
            }
        }

        if (proto.options) {
            props.options = V.Util.extend(L.Util.create(proto.options), props.options);
        }

        V.extend(proto, props);

        return NewClass;

    }

    // V.GeoSearch = {};
    // V.GeoSearch.Provider = {};

    // // jQuery.support.cors = true;

    // V.GeoSearch.Result = function(x,y, label) {
    //     this.X = x;
    //     this.Y = y;
    //     this.Label = label;
    // };

    // V.GeoSearch.Provider.OpenStreetMap = V.Class.extend({
    // options: {

    // },

    // initialize: function(options) {
    //     options = L.Util.setOptions(this, options);
    // },

    // GetServiceUrl: function (qry) {
    //     var parameters = L.Util.extend({
    //         q: qry,
    //         format: 'json'
    //     }, this.options);

    //     return 'http://nominatim.openstreetmap.org/search'
    //         + L.Util.getParamString(parameters);
    // },

    // ParseJSON: function (data) {
    //     if (data.length == 0)
    //         return [];

    //     var results = [];
    //     for (var i = 0; i < data.length; i++) 
    //         results.push(new L.GeoSearch.Result(
    //             data[i].lon, 
    //             data[i].lat, 
    //             data[i].display_name
    //         ));

    //     return results;
    // }
    // });
    this.autoId = 0;
    // An element HTML
    V.Element = V.Class.extend({

        options: {

            // Contain a text div for displaying a message
            // for example error message 
            hasMessage: false
        },

        initialize: function (options) {
            V.extend(this.options, options);
        },

        // @function show
        // set Element visble
        show: function () {
            this._container.style.visibility = 'visible';
        },

        // @function hide
        // set Element invisible
        hide: function () {
            this._container.style.visibility = 'hidden';
        },

        noneDisplay: function () {
            this._container.style.display = 'none';
        },

        display: function () {
            this._container.style.display = 'block';
        },

        setTitle: function (title) {
            if (title)
                this._container.title = title;
            else if (this.options.titleElement)
                this._container.title = this.options.titleElement;
        },

        // @function setMessage(message: String)
        // set messgage to message box
        // example: notify a duplication name
        setMessage: function (message) {
            if (!this._messageBox) {
                // create message box in container in HTML
                this._messageBox =
                    V.create('div', 'message text-basic text-border');
                this._container.appendChild(this._messageBox);
            }
            if (message) {
                this._messageBox.style.display = 'block';
                this._messageBox.innerHTML = message;
            }
            else {
                this._messageBox.style.display = 'none';
            }

        },

        addOn: function (parent) {
            parent.appendChild(this._container);
        },

        addClass: function (className) {
            V.addClass(this._container, className);
        },

        getContainer: function () {
            return this._container;
        },

        // @function setContainer(element: HTMLElement)
        setContainer: function (element) {
            this._container = element;
            this._classOptions();

            return this._container;
        },

        getId: function(element){
            if(!this.id){
                this._container.id = 'autoId'+ thisView.autoId;
                this.id = 'autoId'+ thisView.autoId;
                thisView.autoId++;
            }
            return this.id;
        },

        // @function _classOptions() 
        // Check and add attributs for container 
        _classOptions: function () {
            var options = this.options;
            if (this.options.titleElement)
                this._container.title = this.options.titleElement;
            if (options.class)
                V.addClass(this._container, options.class);
            this._container.id = options.idDiv || '';
            this.id = options.idDiv;
            this._container.style.overflow = options.scroll || 'visible';
            if (options.titleDiv) {
                var firtChild = V.create("div", options.titleDivClass, this._container);
                firtChild.innerHTML = options.titleDiv;
            }
            if (options.parentElement) {
                if (options.parentElement.addChild)
                    options.parentElement.addChild(this._container);
                else
                    options.parentElement.appendChild(this._container);
            }
            if (options.eventClick) {
                L.DomEvent.on(this.getContainer(), 'click', function () {
                    options.eventClick.functionName.call(options.eventClick.className)
                });
            }
        },

        stopEventOfLeaflet: function () {
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
        addChild: function (child) {
            if (child._container)
                child = child._container;
            this._container.appendChild(child);
            if (this.options.childClass) {
                V.addClass(child, this.options.childClass);
            }

            return this;
        },

        addChildToTop: function (child) {
            if (child._container)
                child = child._container;
            this._container.insertBefore(child, this._container.firstChild);
            if (this.options.childClass) {
                V.addClass(child, this.options.childClass);
            }

            return this;
        },

        // @function rmChild(child HTMLelement?V.Class) 
        // Remove a child from container
        rmChild: function (child) {
            if (child._container)
                child = child._container;
            this._container.removeChild(child);
        }



    });

    V.Div = V.Element.extend({

        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
        }

    });

    V.Selector = V.Element.extend({
        initialize: function (options) {
            V.extend(this.options, options);
            this.initSelector();
        },

        initSelector() {
            this._rows = [];
            this._selectorOptions();
            var len = this.rowSource.length;
            for (var i = 0; i < len; i++) {
                // createRow is defined by child class of selector
                this._addRow(this._createRow(this.rowSource[i]));
            }
        },

        _selectorOptions: function () {
            var options = this.options;
            // create shortcut for rowSource
            this.rowSource = options.rowSource || [];

        },

        // @function addRow(element HTMLElement?V.Class)
        // add a Row to selector
        _addRow: function (element) {
            this.addChild(element);
            this._rows.push(element);
        },

        _addRowToTop: function (element) {
            this.addChildToTop(element);
            this._rows.push(element);
        },

        _getIndex: function (DomEl) {
            var i, len = this._rows.length;
            for (i = 0; i < len; i++) {
                if (this._rows[i].getContainer() == DomEl)
                    return i;
            }
        },

        // @function removeRows(index int)
        // remove a Row by index in rows
        removeRow: function (index) {
            // get Element to remove
            var element = this._rows.splice(index, 1)[0];
            // remove from container
            this.rmChild(element);
        },

        // empty the selector: 
        removeAllRow: function () {
            var len = this._rows.length;
            for (var i = len - 1; i >= 0; i--) {
                this.removeRow(i);
            }
        },

        _getIndexById: function (name) {
            var i, len = this._rows.length;
            for (i = 0; i < len; i++) {
                if (this._rows[i].id == name) return i;
            }
        }
    });


    V.SearchBar = V.Element.extend({

        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div', 'searchBar', mapDiv));
            this._searchBarOptions();

            var searchBoxDiv = V.create('div', 'search-box', this._container);
            this.polygonIcon = new V.Icon({
                parentElement: this._container,
                iconChecked: 'fa fa-bandcamp', iconUnchecked: 'fa fa-location-arrow',
                enabled: true, checked: false,
                class: 'poly-icon'
            });
            this.polygonIcon.getContainer().style.position = 'absolute';
            this.polygonIcon.getContainer().style.right = '9px';
            this.polygonIcon.getContainer().style.top = '0px';
            this.polygonIcon.getContainer().style.border = 'none';
            this.polygonIcon.eventHandle = function () {
                this._resultsListDiv.display();
                this._resultsListDiv.setSource(this.geoSearch(this._searchBox.value));
            }.bind(this);
            var searchBox = V.create('input', '', searchBoxDiv);
            searchBox.id = 'searchbox';
            searchBox.type = 'text';
            searchBox.placeholder = this.searchLabel;
            this._searchBox = searchBox;
            var resultsListDiv = new V.ResultListSelector({
                parentElement: this._container, rowSource: [, , , , ,],
                class: "suggestions"
            });
            this._resultsListDiv = resultsListDiv;
            this.currentPoly = L.polygon([]);
            
            this._searchBox.addEventListener('keyup', this._onKeyUp.bind(this), false);
            $('#searchbox').blur(function (e) {
                // this._resultsListDiv.noneDisplay(); 
                // this._resultsListDiv.hide();
                null;
            }.bind(this));
            $('#searchbox').focus(function () {
                // if (myController.editableResearch) {
                //     thisView.locationResearchButton.noneDisplay();
                //     thisView.newPolyAdminButton.noneDisplay();
                // }
                if (this.currentMarker){
                    this.currentMarker.removeFrom(map);
                    this.currentMarker = null;
                }
                if (this.currentPoly){
                    this.currentPoly.removeFrom(map);
                    this.currentPoly.setLatLngs([]);
                }
                // this._resultsListDiv.display();
                this._resultsListDiv.display();
                if (thisView.searchBar.currentMarker)
                    thisView.locationResearchButton.display();
                else 
                    thisView.locationResearchButton.noneDisplay();
                
                if (!thisView.searchBar.currentPoly.isEmpty())
                    thisView.newPolyAdminButton.display();
                else
                    thisView.newPolyAdminButton.noneDisplay();
                // this._resultsListDiv.show();
            }.bind(this));
        },

        geoSearch: function (qry)  {
            var polygon = (this.polygonIcon.checked) ? 1 : 0;
            $.getJSON('http://nominatim.openstreetmap.org/search?format=json&limit=5&q=' + qry + '&polygon=' + polygon, function (data) {
                var items = [];
                var i = 0;
                $.each(data, function (key, val) {
                    items.push(val);
                    i++;
                });
                this._resultsListDiv.setSource(items);
            }.bind(this));
        },

        currentMarker: null,

        currentPoly: null,

        _searchBarOptions: function () {
            var options = this.options;
            this.country = options.country || '';
            this.provider = options.provider;

            this.searchLabel = options.searchLabel || 'Search for address';
            this.zoomLevel = options.zoomLevel || 18
        },

        _onKeyUp: function (e) {
            var escapeKey = 27;
            var enterKey = 13;
            var value = this._searchBox.value;
            this._resultsListDiv.setSource([, , , , ,]);
            if (e.keyCode === escapeKey) {
                this._searchBox.value = '';
                return;
            }

            if (!this.polygonIcon.checked || e.keyCode == enterKey) {
                if (value != '')
                    this.geoSearch(value);
                else
                    this._resultsListDiv.setSource([, , , , , ,]);
            }
        },


    });

    V.ResultListSelector = V.Selector.extend({
        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
            this.getContainer().id = 'list_result';
            this.initSelector();
        },

        // display: function(){
        //     $('list_result').fadeIn("slow");
        // },

        // noneDisplay: function(){
        //     $('list_result').fadeOut("slow");
        // },
        _createRow: function (result) {
            var res = new V.Div({ class: 'suggest' });
            var text = V.create('div', 'suggest-text', res.getContainer());
            res.getContainer().result = result;
            res._text = text;
            res.getContainer().addEventListener('click', this._onClick.bind(this), false);
            if (result)
                text.innerHTML = result.display_name;
            else
                res.noneDisplay();
            return res;
        },

        setSource: function (rowSource) {

            if (rowSource) {
                var i, len = rowSource.length;
                this.rowSource = rowSource;
                for (i = 0; i < len; i++) {
                    if (this.rowSource[i]) {
                        this._rows[i]._text.innerHTML = this.rowSource[i].display_name;
                        this._rows[i].getContainer().result = this.rowSource[i];
                        this._rows[i].display();
                    } else if (this._rows[i])
                        this._rows[i].noneDisplay();
                }
            }

        },


        _onClick: function (e) {
            var target = e.currentTarget;
            if (target.result) {
                var val = target.result;
                if (!thisView.searchBar.currentMarker) {
                    thisView.searchBar.currentMarker = L.marker([val.lat, val.lon]);
                    thisView.searchBar.currentMarker.addTo(map);
                }
                
                var point = L.latLng(val.lat, val.lon);
                thisView.searchBar.currentMarker.setLatLng(point).addTo(map);
                if (myController.editableResearch)
                    thisView.locationResearchButton.display();
                if (val.polygonpoints) {
                    var latlngs = V.Util.reverseArray(val.polygonpoints);
                    // console.log(latlngs.splice(0,400));
                    // console.log(latlngs.splice(0,1));
                    // console.log(simplify(latlngs));
                    
                    thisView.searchBar.currentPoly.setLatLngs(latlngs).addTo(map);
                    map.fitBounds(thisView.searchBar.currentPoly.getBounds());
                    if (myController.editableResearch)
                        thisView.newPolyAdminButton.display();
                }
                else {
                    map.setView(point, 7);
                }
                this.setSource([, , , , ,]);
            }
            this.noneDisplay();
        }


    });



    V.MaplayersSelector = V.Selector.extend({
        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div', 'mapLayersSelector'));
            this.initSelector();
        },

        _createRow: function (layerName) {
            var res = new V.Div({ class: 'row-box' });
            var checkBox = new V.Div({ class: 'roundedOne', parentElement: res });
            var child1 = V.create('input', '', checkBox.getContainer());
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

        check: function (index) {
            var len = this._rows.length;
            for (var i = 0; i < len; i++) {
                this._rows[i].box.checked = (i == index);
            }
            this.currentCheckedBox = this._rows[index].box;
        },

        _onClick: function (e) {
            var target = e.target || e.srcElement;
            this.currentCheckedBox.checked =
                (this.currentCheckedBox == target);
            this.currentCheckedBox = target;
            myController.setBasemap(target.id);
        }

    });

    V.DataDisplaySelector = V.MaplayersSelector.extend({
        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div', 'mapLayersSelector'));
            this.initSelector();
        },

        _onClick: function (e) {
            var target = e.target || e.srcElement;
            this.currentCheckedBox.checked =
                (this.currentCheckedBox == target);
            this.currentCheckedBox = target;
            FILLOPACITY_DISABLED = (target.id == 'Heatmap') ? 0 : 0.4;
            FILLOPACITY_ENABLED = (target.id == 'Heatmap') ? 0 : 0.2;
            myController.setDisplayType(target.id);
        }
    });

    V.UserLayersButtons = V.Element.extend({
        initialize: function(options){
            V.extend(this.options, options);

            var iconsBarre = new V.Div({ class: 'user-layers-buttons'});
            this.setContainer(iconsBarre.getContainer());            
            this.trashIcon = new V.TrashIcon({
                checked: true, enabled: true,
                parentElement: iconsBarre
            });
            
            this.exportationIcon = new V.ExportationIcon({
                checked: true,
                enabled: true,
                parentElement: iconsBarre
            });
            
            this.exportationIcon.eventHandle = this._exportation.bind(this);
        },

        _exportation: function(){
            myController.exportation(myController.rois,'LoadedPoint', false);
            this.exportationIcon.setChecked();
        }


    });

    V.UserLayersSelector = V.Selector.extend({
        options: {
            rowSource: myModel.researches
        },

        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
            this.initSelector();
            this.buttons = new V.UserLayersButtons({parentElement: this});
            this.buttons.trashIcon.eventHandle = this._removeAllResearch.bind(this);
        },

        _createRow: function (research) {
            var row = new V.Div({
                class: 'nice-box row-researches-panel'
            });
            var iconsBarre = new V.Div({ class: 'iconsBarre', parentElement: row });
            row.plusIcon = new V.PlusIcon({
                checked: true, enabled: true,
                parentElement: row, idDiv: "plus " + research.nameResearch
            });
            var researchIcon = new V.Icon({
                parentElement: row, enabled: false,
                iconChecked: 'fa fa-tasks', iconUnchecked: 'fa fa-tasks',
                clearBackground: true, checked: true, class: 'researchIcon',
                idDiv: 'resch' + research.nameResearch
            });
            row.researchIcon = researchIcon;
            row.nameResearch = V.create('p', 'normal-text', row.getContainer());
            row.nameResearch.innerHTML = research.nameResearch;
            row.eyeIcon = new V.EyeIcon({
                checked: false, enabled: true,
                parentElement: iconsBarre,
                idDiv: "eye  " + research.nameResearch
            });
            row.trashIcon = new V.TrashIcon({
                checked: true, enabled: true,
                parentElement: iconsBarre,
                idDiv: "trash" + research.nameResearch
            });
            row.editionIcon = new V.EditionIcon({
                checked: false, enabled: true,
                parentElement: iconsBarre,
                idDiv: "editi" + research.nameResearch
            });
            row.exportationIcon = new V.ExportationIcon({
                checked: true,
                enabled: true, idDiv: 'expt ' + research.nameResearch,
                parentElement: iconsBarre
            });
            row.roiSelector = new V.RoiSelector({
                rowSource: research.roi,
                parentElement: row
            });
            row.trashIcon.eventHandle = this._removeResearch.bind(this);
            row.editionIcon.eventHandle = this._editResearch.bind(this);
            row.eyeIcon.eventHandle = this._hideResearch.bind(this);
            row.plusIcon.eventHandle = this._hideRoiSelector.bind(this);
            researchIcon.eventHandle = this._setView.bind(this);
            row.exportationIcon.eventHandle = this._exportation.bind(this);
            //row.trashIcon.getContainer().addEventListener('click',
            //                    this._removeResearch.bind(this), false);
            row.id = research.nameResearch;
            
            return row;
        },

        checkedEditionIcon: function () {
            // if there are no editable Research
            if (!myController.editableResearch)
                return;
            var i = this._getIndexById(myController.editableResearch.nameResearch);
            // if rows[i] is removed from researches panel
            if (i == null)
                return;
            this._rows[i].editionIcon.check();

        },

        enableResearchIcon: function () {
            var i = this._getIndexById(myController.editableResearch.nameResearch);
            this._rows[i].researchIcon.enable();
        },

        addRow: function (research) {
            this.checkedEditionIcon();
            var el = this._createRow(research);
            this._addRowToTop(el);
            el.getContainer().style.backgroundColor = research.colorBackground;
            el.editionIcon.check();

        },

        addUnderRow: function (research, layer) {
            var i = this._getIndexById(research.nameResearch);
            this._rows[i].roiSelector.addRow(layer);
        },

        removeUnderRow: function (research, layer) {
            var i = this._getIndexById(research.nameResearch);
            this._rows[i].roiSelector.removeRowByLayer(layer);
        },

        changeBackground: function (research, color) {
            var i = this._getIndexById(research.nameResearch);
            this._rows[i].getContainer().style.backgroundColor = V.Util.convertColor(color, 0.6);
        },

        changeBorder: function (research, color) {
            var i = this._getIndexById(research.nameResearch);
            this._rows[i].getContainer().style.borderColor = color;
        },

        _editResearch: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            if (button.checked) {
                // uncheck previous editable research
                this.checkedEditionIcon(i);
                // display polygons of editable research et disable eye icon
                this._rows[i].eyeIcon.disable();
                if (!this._rows[i].eyeIcon.checked)
                    this._rows[i].eyeIcon.check();
                // add border to the current editable research row
                this._rows[i].getContainer().style.border = 'solid black';
                myController.changeEditableResearch(i);
                this._rows[i].roiSelector.enableTrashIcons();
            }
            else {
                this._rows[i].eyeIcon.enable();
                // remove border of previous editable research row
                this._rows[i].getContainer().style.border = 'none';
                myController.changeEditableResearch(-1);
                this._rows[i].roiSelector.disableTrashIcons();
            }
        },

        _removeResearch: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            this.removeRow(i);
            myController.removeResearch(i);
            myController.actualize();
        },

        _removeAllResearch: function(){
            var len = this._rows.length;
            for(var i=len-1 ;i>=0 ;i--){
                this.removeRow(i);
                myController.removeResearch(i);
            }
            myController.actualize();
            myView.researchesPanel.buttons.trashIcon.setChecked();
        },

        _hideResearch: function (button) {
            var layer, j, i = this._getIndexById(button.id.slice(5));
            if (button.checked) {
                this._rows[i].roiSelector.enableEyeIcons();
            }
            else {
                this._rows[i].roiSelector.disableEyeIcons();
            }
        },

        _hideRoiSelector: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            if (this._rows[i].plusIcon.checked)
                this._rows[i].roiSelector.display();
            else
                this._rows[i].roiSelector.noneDisplay();
        },

        _setView: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            var research = this.rowSource[i];
            map.setView(research.locationMarker.getLatLng(), 7);
        },

        _exportation: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            var research = this.rowSource[i];
            myController.exportation(research.roi, research.nameResearch, true);
            button.setChecked();
        },

        _convertArrayOfObjectsToCSV: function (args) {
            var result, ctr, keys, columnDelimiter, lineDelimiter, data;
            console.log(args.data);

            data = args.data || null;
            if (data == null || data.list == null) {
                return null;
            }
            columnDelimiter = args.columnDelimiter || ',';
            lineDelimiter = args.lineDelimiter || '\n';

            keys = data.key;

            result = '';
            result += keys.join(columnDelimiter);
            result += lineDelimiter;
            var nbCol = keys.length;

            data.list.forEach(function (item) {
                ctr = 0;
                for (var i = 0; i < nbCol; i++) {
                    if (ctr > 0) result += columnDelimiter;

                    result += item[i];
                    ctr++;
                };
                result += lineDelimiter;
            });
            console.log(result);
            return result;
        },

        _downloadCSV: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            // var stockData = [  
            //     {
            //         Symbol: "AAPL",
            //         Company: "Apple Inc.",
            //         Price: 132.54
            //     },
            //     {
            //         Symbol: "INTC",
            //         Company: "Intel Corporation",
            //         Price: 33.45
            //     },
            //     {
            //         Symbol: "GOOG",
            //         Company: "Google Inc",
            //         Price: 554.52
            //     },
            // ];
            var stockData = {
                key: ['Symbol', 'Company', 'Price'],
                list: [
                    ["AAPL", "Apple Inc.", 132.54],
                    ["INTC", "Intel Corporation", 33.45],
                    ["AAPL", "Apple Inc.", 132.54]]
            };
            var data, filename, link;
            var csv = this._convertArrayOfObjectsToCSV({
                data: stockData
            });
            if (csv == null)
                return;

            filename = button.id.slice(5) + '.csv';

            var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

            if (navigator.msSaveBlob) { // IE 10+
                navigator.msSaveBlob(blob, filename)
            }
            else {
                var link = document.createElement("a");
                if (link.download !== undefined) {
                    // feature detection, Browsers that support HTML5 download attribute
                    var url = URL.createObjectURL(blob);
                    link.setAttribute("href", url);
                    link.setAttribute("download", filename);
                    link.style = "visibility:hidden";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        }
    });

    V.RoiSelector = V.Selector.extend({

        initialize: function (options) {
            V.extend(this.options, options);
            this.setContainer(V.create('div'));
            this.initSelector();
        },

        _createRow: function (layer) {
            var row = new V.Div({
                class: ' nice-box row-roi'
            });
            var iconsBarre = new V.Div({ class: 'iconsBarre', parentElement: row });
            var icon = (layer.editor) ? 'fa fa-paint-brush' : 'fa fa-bandcamp';
            var polyIcon = new V.Icon({
                parentElement: row, enabled: true,
                iconChecked: icon, iconUnchecked: icon,
                checked: true, class: 'researchIcon',
                clearBackground: true, idDiv: "poly " + layer.namePoly
            });
            row.namePoly = V.create('p', 'normal-text', row.getContainer());
            row.namePoly.innerHTML = layer.namePoly;
            row.eyeIcon = new V.EyeIcon({
                class: 'small-icon', checked: true, enabled: true,
                parentElement: iconsBarre,
                idDiv: "eye  " + layer.namePoly
            });
            row.trashIcon = new V.TrashIcon({
                class: 'small-icon', checked: true, enabled: true,
                parentElement: iconsBarre,
                idDiv: "trash" + layer.namePoly
            });
            row.eyeIcon.eventHandle = this._hidePolygon.bind(this);
            row.trashIcon.eventHandle = this._removePolygon.bind(this);
            polyIcon.eventHandle = this._fitBounds.bind(this);
            row.id = layer.namePoly;
            return row;
        },

        addRow: function (layer) {
            var el = this._createRow(layer);
            this._addRow(el);
        },

        removeRowByLayer: function (layer) {
            var i = this._getIndexById(layer.namePoly);
            this.removeRow(i);
        },

        enableTrashIcons: function () {
            var i, len = this.rowSource.getLayers().length;
            for (i = 0; i < len; i++) {
                this._rows[i].trashIcon.enable();
            }
        },

        disableTrashIcons: function () {
            var i, len = this.rowSource.getLayers().length;
            for (i = 0; i < len; i++) {
                this._rows[i].trashIcon.disable();
            }
        },

        enableEyeIcons: function () {
            var layer, i, len = this.rowSource.getLayers().length;
            for (i = 0; i < len; i++) {
                this._rows[i].eyeIcon.enable();
                layer = this.rowSource.getLayers()[i];
                if (this._rows[i].eyeIcon.checked)
                    myController.showPolygonToGUI(layer);
            }
            myController.actualize();
        },

        disableEyeIcons: function () {
            var layer, i, len = this.rowSource.getLayers().length;
            for (i = 0; i < len; i++) {
                this._rows[i].eyeIcon.disable();
                layer = this.rowSource.getLayers()[i];
                if (this._rows[i].eyeIcon.checked)
                    myController.hidePolygonFGUI(layer);
            }
            myController.actualize();
        },

        _removePolygon: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            var layer = this.rowSource.getLayers()[i];
            // var poly;
            // if (layer.editor) {
            //     poly = layer.editor.deleteShape(layer.getLatLngs());
            // } else {
            //     poly = layer;
            // }
            myController.deletePolygon(layer);
            myController.actualize();
        },

        _hidePolygon: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            var layer = this.rowSource.getLayers()[i];
            if (this._rows[i].eyeIcon.checked)
                myController.showPolygonToGUI(layer);
            else
                myController.hidePolygonFGUI(layer);
            myController.actualize();
        },

        _fitBounds: function (button) {
            var i = this._getIndexById(button.id.slice(5));
            var layer = this.rowSource.getLayers()[i];
            map.fitBounds(layer.getBounds());
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
                V.create('input', '', this._container);
            textBox.id = this._tbid;
            textBox.type = 'text';
            textBox.placeholder = this._textdefault;
            this._textBox = textBox;

            this._submitButton = new V.PlusIcon({
                iconChecked: 'fa fa-plus',
                enabled: true, checked: true, parentElement: this._container
            });


            this._textBox.addEventListener('keyup', this._onKeypressed, false);

        },

        textboxOptions: function () {
            var options = this.options;
            this._tbid = options.tbid || '';
            this._textdefault = options.textdefault || '';

        },

        // get current text in the box
        getValue: function () {
            return this._textBox.value;
        },

        // reset Value of text box to default
        setValue: function (name) {
            this._textBox.value = name;
        },

        disable: function () {
            this._submitButton.getContainer().removeEventListener('click',
                this._onClick, false);
            this._submitButton.disable();
        },

        enable: function () {
            this._submitButton.getContainer().addEventListener('click',
                this._onClick, false);
            this._submitButton.enable();
        },
        // update data when text box is changed
        _onClick: function (e) {
            myController.addResearch();
        },

        _onKeypressed: function () {
            myController.actualize();
        }


    });


    // this.nameBox = 
    //     thisView.createTextBox(map,"ResearchBox", "Current Research");

    // Notice: O
    V.Button = V.Element.extend({

        initialize: function (options) {
            V.extend(this.options, options);
            var container = this.setContainer(V.create('div', 'leaflet-bar')),
                link = V.create('a', '', container);
            this._container = container;
            this.setTitle();
            this._link = link;

            // div attributs
            link.href = '#';
            link.innerHTML = this.options.sign;

            return container;
        },

        getLink: function () {
            return this._link;
        },
        invisible: function (bool) {
            if (bool) this._container.style.visibility = 'hidden';
            else this._container.style.visibility = 'visible';
        },

        setSign: function (sign) {
            this._link.innerHTML = sign;
        }
    });

    V.Icon = V.Element.extend({
        initialize: function (options) {
            V.extend(this.options, options);
            this.initIcon();
        },

        initIcon: function () {
            this.setContainer(V.create('div', 'icon'));
            this._iconOptions();
            var className = (this.checked) ? this.iconChecked : this.iconUnchecked;
            this._icon = V.create('i', className, this._container);
            (this.enabled) ? this.enable() : this.disable();
        },

        disable: function () {
            //if(this.checked) this._onClick();
            this._container.style.backgroundColor = 'transparent';
            this.enabled = false;
            this._container.style.cursor = 'initial';
            this._container.style.boxShadow = '';
            V.DomUtil.removeClass(this._container, 'enabled');
            V.DomUtil.removeClass(this._container, 'checked');
            V.DomUtil.removeClass(this._container, 'unchecked');
            if (!this._maskOnClick) this._maskOnClick = this._onClick.bind(this);
            this._container.removeEventListener('click',
                this._maskOnClick, false);
        },

        enable: function () {
            this._container.style.backgroundColor = 'white';

            this.enabled = true;
            if (!this._maskOnClick) this._maskOnClick = this._onClick.bind(this);
            this._container.addEventListener('click',
                this._maskOnClick, false);
            this._container.style.cursor = 'pointer';
            V.DomUtil.addClass(this._container, 'enabled');
            if (this.clearBackground) {
                this._container.style.backgroundColor = 'transparent';
                this._container.style.boxShadow = '';
                this._container.style.border = 'none';
                return;
            }
            // this._container.style.boxShadow 
            //  ='inset 0px 1px 1px white, 0px 1px 3px rgba(0, 0, 0, 0.5)';
            if (this.checked) {
                V.DomUtil.removeClass(this._container, 'unchecked');
                V.DomUtil.addClass(this._container, 'checked');
            } else {
                V.DomUtil.removeClass(this._container, 'checked');
                V.DomUtil.addClass(this._container, 'unchecked');
            }
        }
        ,

        _iconOptions: function () {
            var options = this.options;

            this.iconUnchecked = options.iconUnchecked || 'fa fa-bath';
            this.iconChecked = options.iconChecked || 'fa fa-bath';
            this.checked = options.checked;
            this.index = options.index || -1;
            this.enabled = options.enabled;
            this.clearBackground = options.clearBackground || false;
        },

        // attention: eventHandle will be defined by button
        _onClick: function () {
            this.setChecked();
            this.eventHandle(this);
        },

        setChecked: function(){
            this.checked = !this.checked;
            var className = (this.checked) ? this.iconChecked : this.iconUnchecked;
            V.DomUtil.setClass(this._icon, className);
            if (!this.enabled) {
                V.DomUtil.removeClass(this._container, 'unchecked');
                V.DomUtil.removeClass(this._container, 'checked');
                return;
            }
            if (this.checked) {
                V.DomUtil.removeClass(this._container, 'unchecked');
                V.DomUtil.addClass(this._container, 'checked');
            } else {
                V.DomUtil.removeClass(this._container, 'checked');
                V.DomUtil.addClass(this._container, 'unchecked');
            }
        },

        check: function () {
            this._onClick();
        },

        getIcon: function () {
            return this._icon;
        },

        eventHandle: function () {
            null
        }
    });

    V.PlusIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-plus',
            iconChecked: 'fa fa-minus'
        },
        initialize: function (options) {

            V.extend(this.options, options);
            this.initIcon();
        },
        eventHandle: function (button) {
            null
        }
    });

    V.EyeIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-eye-slash',
            iconChecked: 'fa fa-eye'
        },
        initialize: function (options) {

            V.extend(this.options, options);
            this.initIcon();
            this.isEye = true;
            this._icon.style.left = "-1px";
        },
        eventHandle: function (button) {
            null
        }
    });

    V.EditionIcon = V.Icon.extend({
        options: {
            iconChecked: 'fa fa-pencil-square',
            iconUnchecked: 'fa fa-pencil'
        },
        initialize: function (options) {
            V.extend(this.options, options);
            this.initIcon();
        },
        eventHandle: function () {
            null
        }
    });

    V.TrashIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-trash',
            iconChecked: 'fa fa-trash'
        },
        initialize: function (options) {
            V.extend(this.options, options);
            this.initIcon();
        },
        eventHandle: function () {
            null
        }
    });

    V.ExportationIcon = V.Icon.extend({
        options: {
            iconUnchecked: 'fa fa-cloud-download',
            iconChecked: 'fa fa-cloud-download'
        },
        initialize: function (options) {
            V.extend(this.options, options);
            this.initIcon();
            this._icon.style.left = "-2px";
        },
        eventHandle: function () {
            null
        }
    });


    V.ColorSelector = V.Element.extend({

        initialize: function (options) {
            options = V.extend(this.options, options);

            // container div in HTML
            var container = this.setContainer(V.create('div'));

            var select = V.create('div', 'nice-box', container);
            select._showList = false;
            var selectedColor = new V.Div({ parentElement: select, class: "nice-box colorRow" });
            this._selectedColor = selectedColor;
            var list = new V.Div({ parentElement: select, class: "colorList" });
            list.noneDisplay();
            this._select = select;
            this._selectedColor.getContainer().addEventListener('click',
                function () {
                    // check if window is too small for display selection list
                    if (window.innerHeight < 500)
                        thisView.editionDiv.getContainer().style.overflow = "auto";
                    else
                        thisView.editionDiv.getContainer().style.overflow = "visible";

                    select._showList = !select._showList;
                    if (!select._showList)
                        list.noneDisplay();
                    else
                        list.display();
                }, false);

            for (var i = 0; i < this.options.listColor.length; i++) {
                var option = new V.Div({ parentElement: list, class: "nice-box colorRow" });
                option.getContainer().valueColor = this.options.listColor[i];
                option.getContainer().style.backgroundColor = this.options.listColor[i];
                option.getContainer().addEventListener('click', function (e) {
                    select.valueColor = e.currentTarget.valueColor;
                    select.style.background = e.currentTarget.valueColor;
                    select._showList = false;
                    list.noneDisplay();
                    myController.actualize();
                }, false);
            }
            //select.style.background = select.options[select.selectedIndex].value;
            //select.style.color = select.options[select.selectedIndex].value;
            // select.addEventListener('change', 
            //     function(){ myController.actualize(); }, false );

            // check if window is too small

            return select;
        },

        getSelect: function () {
            return this._select;
        },

        getColor: function () {
            return this._select.valueColor;
        },

        setColor: function (color) {
            this._select.style.background = color;
            this._select.style.color = color;
            this._select.valueColor = color;
        }
    });

    V.DataLoadingBar = V.Element.extend({
        initialize: function(options){
            options = V.extend(this.options, options);

            // container div in HTML
            var container = this.setContainer(V.create('div','loadingbox'));
            this._loadingBarOptions();
            this.loadingBar = V.create('div', 'loadingbar', this.getContainer());
            this.loadedBar = V.create('div', 'loadedbar', this.loadingBar);
        },

        update: function(){
            var long = myController.loadedPoint;
            var   loadedLong = myController.exportationUtil.count;
            this.loadedBar.style.width = (loadedLong/long)*100 + '%';
            this.setMessage('Loading '+ loadedLong +'/'+long);    
        },

        _loadingBarOptions: function () {
            var options = this.options;

            this.iconUnchecked = options.iconUnchecked || 'fa fa-bath';
            this.long = options.long || 100.0;
            this.loadedLong = options.loadedLong || 0.0;
        }

    });

    V.Loader = V.Element.extend({
        initialize: function(options){
            options = V.extend(this.options, options);

            // container div in HTML
            this.setContainer(V.create('div','loaderbox'));
            V.create("div", 'loader', this._container);
            this.loadedPoint = V.create('p','text-basic',this._container);
        },

        update: function(){
            this.loadedPoint.innerHTML = 'Loaded '+ myController.exportationUtil.count;
        }
    });

    this.dataLoadingBar = new V.DataLoadingBar({parentElement: document.getElementById('layout')});
    this.loader = new V.Loader({parentElement: document.getElementById('layout')});

    //--------------------------------------Instances----------------------------------------------

    var deleteShape = function (e) {
        if ((e.originalEvent.ctrlKey || e.originalEvent.metaKey) && this.editEnabled()) {
            var poly = this.editor.deleteShapeAt(e.latlng);
            myController.deletePolygon(poly);
        }
    };
    // map.on('layeradd', function (e) {
    //     if (e.layer instanceof L.Path) e.layer.on('click', L.DomEvent.stop).on('click', deleteShape, e.layer);
    //     if (e.layer instanceof L.Path) e.layer.on('dblclick', L.DomEvent.stop).on('dblclick', e.layer.toggleEdit);
    // });

    // when finish drawing
    map.on('editable:drawing:end', function (e) {
        // save Poly
        e.namePoly = '';
        myController.registerPoly(e.layer);
        e.layer.bindTooltip(e.layer.namePoly).openTooltip();
        e.layer.getTooltip().setOpacity(1);
        e.layer.on('dragend', function () {
            myController.actualize();
        });
        e.layer.on('editable:vertex:dragend', function (e) {
            myController.actualize();
        });
        e.layer.on('editable:vertex:deleted', function(e){
            myController.actualize();
        });
        hideResearch();
    
        myController.actualize();

    });



    /**
     *  LayerGroup contain all ROIs displayed on Map 
     *  including polygons:
     *  + Polygons of research
     *  + ROI admin (not implemented)
     */
    // this.rois =
    //     new L.LayerGroup;
    // this.rois.addTo(map);

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
     * Edit box div 
     * Position: left
     * id = research
     * see research.css
     */
    var mapDiv = document.getElementById('map')
    this.editionDiv = new V.Div({
        parentElement: mapDiv, class: "nice-box normal-text",
        childClass: 'champComposant nice-box', idDiv: 'research'
    });
    this.editionDiv.show = function () {
        thisView.editionDiv.getContainer().style.visibility = 'visible';
    }
    // hide varable
    this.editionDiv.hideState = true;
    this.editionDiv.stopEventOfLeaflet();

    // research name
    this.editionTitle = new V.Div({ class: ' text-basic text-border edition-title', parentElement: mapDiv });
    this.editionTitle.getContainer().innerHTML = 'Name research';
    // hide div
    function hideResearch() {

        if (thisView.editionDiv.hideState == true) {
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

    this.editionHide = new V.Button({
        sign: '◄', titleElement: 'Hide research',
        class: 'hideResearch', parentElement: mapDiv
    });
    L.DomEvent.on(this.editionHide.getLink(), 'click', hideResearch);

    //--------------- Fill Editiontools box --------------------



    var editBox = new V.Div({
        titleDiv: "Edition Tools", parentElement: this.editionDiv,
        childClass: 'childOfEditTools',
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });

    var timeBox = new V.Div({
        titleDiv: "Time Interval", parentElement: this.editionDiv,
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });
    var colorBox = new V.Div({
        titleDiv: "Color Selections", parentElement: this.editionDiv,
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });

    this.setLocation = function () {
        var l = this.searchBar.currentMarker.getLatLng();

        if (!myController.editableResearch.locationMarker) {
            myController.editableResearch.locationMarker =
                L.marker([l.lat, l.lng], {
                    icon: L.AwesomeMarkers.icon({
                        icon: 'coffee',
                        markerColor: V.Util.convertMarkerColor(myController.editableResearch.colorBackground),
                        prefix: 'fa', iconColor: 'black'
                    })
                }).addTo(map);
            myView.researchesPanel.enableResearchIcon();
        }
        else
            myController.editableResearch.locationMarker.setLatLng(l);
        this.searchBar.currentMarker.removeFrom(map);
        this.locationResearchButton.noneDisplay();
    }
    this.locationResearchButton = new V.Button({
        sign: '⚀', titleElement: 'Set Location',
        parentElement: editBox,
        eventClick: {
            className: thisView, functionName:
                thisView.setLocation
        }
    });
    // this.locationResearchButton.noneDisplay();

    /**
    *  Add button for creating a zone
   */
    this.newPolygonButton = new V.Button({
        sign: '▱', titleElement: 'New polygon',
        parentElement: editBox,
        eventClick: {
            className: map.editTools, functionName:
                map.editTools.startPolygon
        }
    });
    $('#'+this.newPolygonButton.getId()).click(hideResearch);
    this.newRectangleButton = new V.Button({
        sign: '▭', titleElement: 'New rectangle',
        parentElement: editBox,
        eventClick: {
            className: map.editTools, functionName:
                map.editTools.startRectangle
        }
    });
    $('#'+this.newRectangleButton.getId()).click(hideResearch);
    
    this.newCircleButton = new V.Button({
        sign: '◯', titleElement: 'New Circle',
        parentElement: editBox,
        eventClick: {
            className: map.editTools, functionName:
                map.editTools.startCircle
        }
    });
    $('#'+this.newCircleButton.getId()).click(hideResearch);
    /**
    *  Add button for reset current research
    */
    // this.resetResearchButton = new V.Button({sign: '♺', titleElement: 'Reset Research',
    //                         parentElement: editBox});

    this.addPolyAdmin = function () {
        var l = this.searchBar.currentPoly.getLatLngs();
        var layer =
            L.polygon(l, {
                color: myController.editableResearch.colorBorder
                , fillColor: myController.editableResearch.colorBackground,
                fillOpacity: 0.2, weight: WEIGHT_ROI
            })
                .addTo(map);
        myController.registerPoly(layer);
        layer.enableEdit();
        layer.on('dragend', function () {
            myController.actualize();
        });
        layer.on('editable:vertex:dragend', function (e) {
            myController.actualize();
        });
        layer.on('editable:vertex:deleted', function(e){
            myController.actualize();
        });
        layer.bindTooltip(layer.namePoly).openTooltip();
        layer.getTooltip().setOpacity(1);
        this.searchBar.currentPoly.removeFrom(map);
        this.searchBar.currentPoly.setLatLngs([]);
        this.newPolyAdminButton.noneDisplay();
        myController.actualize();
    }
    this.newPolyAdminButton = new V.Button({
        sign: '▶', titleElement: 'Add Polygon',
        parentElement: editBox,
        eventClick: {
            className: thisView, functionName:
                thisView.addPolyAdmin
        }
    });
    // this.newPolyAdminButton.noneDisplay();




    //---------------Fill TimeInterval box-------------------

    V.timeSelector = V.Element.extend({
        options: {
            hasMessage: true
        },


        initialize: function (text, date, month, year, parent) {
            var container = V.create('div', 'timeSelector', parent);
            this._container = container;
            this._textDiv = V.create('div', '', container);
            this._textDiv.innerHTML = text;
            this._dateDiv = L.DomUtil.create('select', '', container);
            for (var i = 1; i < 31; i++) {
                var option = L.DomUtil.create('option', 'timeOption', this._dateDiv);
                option.text = i;

            }

            this._dateDiv.defaultValue = date;
            this._dateDiv.text = date;
            this._dateDiv.value = date;

            this._monthDiv = L.DomUtil.create('select', '', container);
            for (var i = 0; i < this.monthsShort.length; i++) {
                var option = L.DomUtil.create('option', 'timeOption', this._monthDiv);
                option.text = this.monthsShort[i];
            }
            this._monthDiv.defaultValue = month;
            this._monthDiv.value = month;

            this._yearDiv = L.DomUtil.create('select', '', container);
            for (var i = 2007; i <= 2017; i++) {
                var option = L.DomUtil.create('option', 'timeOption', this._yearDiv);
                option.text = i;
            }
            this._yearDiv.defaultValue = year;
            this._yearDiv.value = year;



            return this;
        },

        monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],

        getDate: function () {
            return this._dateDiv.value;
        }

    });

    this.startTimetDiv = new V.timeSelector("Start", 23, 'Dec', 2017);
    this.endTimetDiv = new V.timeSelector("End", 23, 'Dec', 2017);

    timeBox.addChild(this.startTimetDiv).addChild(this.endTimetDiv);

    //-------------------Fill Color Selector--------------------------------//
    /**
     *  Add background color selector 
     */
    // var colors = ['OliveDrab','Red', 'Orange', 'Yellow', 'Green', 'LightSkyBlue ' , 'Blue' , 'Purple' ];
    // attention: format of color : '*x.y)' 
    var colors = ['rgba(107, 142, 35, 1.0)', 'rgba(255, 0, 0, 1.0)', 'rgba(255, 165, 0, 1.0)', 'rgba(255, 192, 203, 1.0)', 'rgba(0, 128, 0, 1.0)', 'rgba(135, 206, 250, 1.0)', 'rgba(0, 0, 255, 1.0)', 'rgba(128, 0, 128, 1.0)'];
    this.colors = colors;
    this.backgroundColorSelector = new V.ColorSelector({
        listColor: colors,
        titleElement: 'Background Color'
    });

    this.borderColorSelector = new V.ColorSelector({
        listColor: colors,
        titleElement: 'Border Color'
    });

    /**
     *  Add tweets color selector 
     */
    this.tweetsColorSelector = new V.ColorSelector({
        listColor: colors,
        titleElement: 'Tweets Color'
    });

    function addColorSelector(text, child, parent) {

        var container = V.create('div', 'colorSelector', parent);

        var textDiv = V.create('div', 'normal-text', container);
        textDiv.innerHTML = text;
        var colorSelector = child;
        container.appendChild(colorSelector);

        return container;
    }

    addColorSelector('Background', thisView.backgroundColorSelector.getContainer(), colorBox.getContainer());
    addColorSelector('Border', thisView.borderColorSelector.getContainer(), colorBox.getContainer());
    addColorSelector('Tweets', thisView.tweetsColorSelector.getContainer(), colorBox.getContainer());

    /**
     * Recherche Management box div 
     * Position: right
     * id = management
     * see management.css
     */
    this.managementDiv = new V.Div({
        class: "nice-box",
        parentElement: mapDiv, childClass: ' champComposant nice-box',
        idDiv: "management", scroll: 'auto'
    });
    thisView.managementDiv.show();

    this.managementDiv.stopEventOfLeaflet();
    // hide varable

    // hide varable
    this.managementDiv.hideState = true;

    function hideManangement() {

        if (thisView.managementDiv.hideState == true) {
            thisView.managementDiv.hide();
            thisView.hideManagementButton.setTitle('Show management');
            thisView.hideManagementButton.setSign("◄");
            thisView.hideManagementButton.getContainer().style.right = '0px';
        }
        else {
            thisView.managementDiv.show();
            thisView.hideManagementButton.setTitle('Hide management');
            thisView.hideManagementButton.setSign("►");
            thisView.hideManagementButton.getContainer().style.right = '33%';

        }
        thisView.managementDiv.hideState = !thisView.managementDiv.hideState;

    }
    this.hideManagementButton = new V.Button({
        sign: '►', titleElement: 'Hide management',
        class: 'hideManagement', parentElement: mapDiv
    });

    // L.DomEvent.on(this.hideManagementButton.getContainer(), 'click', hideManangement);
    $("#"+this.hideManagementButton.getId()).on( "click", hideManangement);

    this.baseMapsBox = new V.Div({
        titleDiv: "Base Maps", parentElement: this.managementDiv,
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });
    this.dataDisplayBox = new V.Div({
        titleDiv: "Data Display", parentElement: this.managementDiv,
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });
    this.userlayersBox = new V.Div({
        titleDiv: "User Layer", parentElement: this.managementDiv,
        titleDivClass: 'underChampComposant title text-border firstComposant'
    });

    //----------------------Fill basemapsBox----------------------------------------/
    this.mapLayersSelector = new V.MaplayersSelector({
        parentElement: this.baseMapsBox, class: 'normal-text',
        rowSource: Object.keys(myModel.mapLayers.dict)
    });

    //----------------------Fill dataDisplayBox----------------------------------------/
    this.dataDisplaySelector = new V.DataDisplaySelector({
        parentElement: this.dataDisplayBox, class: 'normal-text',
        rowSource: ['Heatmap', 'Cluster']
    });

    //----------------------Fill userlayersBox-------------------------------------/
    this.nameBox = new V.TextBox({ tbid: 'ResearchBox', textdefault: 'Name' });
    this.userlayersBox.addChild(this.nameBox);
    this.researchesPanel = //new V.Div({parentElement: this.userlayersBox, class: 'researches-panel'});
        new V.UserLayersSelector({
            parentElement: this.userlayersBox,
            class: 'researches-panel'
        });

    this.searchBar = new V.SearchBar({});
    this.searchBar.stopEventOfLeaflet();

    //-----------------------Data info box----------------------------------------
    this.infobox = L.control();

    this.infobox.onAdd = function (map) {
        this._div = V.create('div', 'infobox'); // create a div with a class "infobox"
        this._div.id = 'infobox'
        return this._div;
        
    };

    // method that we will use to update the control based on feature properties passed
    this.infobox.update = function (props) {
        this._div.innerHTML = props.text + ' ' +
            '<i class="fa fa-' + props.icon + '"></i>';
    };

    this.infobox.addTo(map);

}

//---------------------------------------View Singleton-----------------------------------------------/
var myView = new View();

