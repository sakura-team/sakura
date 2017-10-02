var WEIGHT_ROI = 2; 
var FILLOPACITY_DISABLED = 0;
var FILLOPACITY_ENABLED = 0;
var HEATMAP_RADIUS = 15;
var HEATMAP_REFRESH_DELAY = 0.3;
var EXPORTATION_REFRESH_DELAY = 0.003;
// Wordcloud configuration
// Pour Tester https://timdream.org/wordcloud2.js/#love 
var WORDCLOUD_OPTION_CONF = {
    gridSize: 40,
    weightFactor: 4,
    fontFamily: 'Average, Times, serif',
    color: function() {
      return (['#d0d0d0', '#e11', '#44f'])[Math.floor(Math.random() * 3)]
    },
    backgroundColor:     '#333'
};