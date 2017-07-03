/**
 * Unit Testing
 */

// Test GUI
// test addResearch
var i=1;
myController.addResearch();
myController.addResearch();
console.log(i+++"--------------------------------------------------");
console.log("Added two researches");
console.log("Expected result: 2 researches");
console.log(myController.toString());
console.log(i+++"--------------------------------------------------");
myController.removeResearchByIndex(0);
console.log("Removed first research");
console.log("Expected result: 1 researches");
console.log(myController.toString());
console.log(i+++"--------------------------------------------------");
myController.addResearch();
console.log("Added a research");
console.log("Expected result: 2 researches");
console.log(myController.toString());
console.log(i+++"--------------------------------------------------");
myController.removeResearchByIndex(1);
console.log("Removed current Research");
console.log("Expected result: 2 researches");
console.log(myController.toString());
console.log(i+++"--------------------------------------------------");
console.log("Infor of current research");
console.log("Expected result: Research of Rid = 4");
console.log(myModel.currentResearch.toString());
console.log(i+++"--------------------------------------------------");
console.log("Get infor of a research");
console.log("Expected result: Research infor of research of Rid = 2");
console.log(myController.getResearchByRid(2).toString());
console.log(i+++"--------------------------------------------------");
myController.getResearchByRid(2).colorPoint = "blue";
console.log("Changed colorPoint of research of Rid = 2 to blue")
console.log("Expected result: Research infor updated colorPoint");
console.log(myController.getResearchByRid(2).toString());
console.log(i+++"--------------------------------------------------");
myController.getResearchByRid(4).nameResearch = "Paris";
console.log("Changed name of research of Rid = 4 to Paris")
console.log("Expected result: Research infor updated name");
console.log(myController.getResearchByRid(4).toString());
console.log(i+++"--------------------------------------------------");
myController.changeCurrentResearchByRid(rid = 2);
console.log("Changed current research by rid to research of rid = 2")
console.log("Expected result: color of research of rid = 2 reupdated point color to green");
console.log(myController.toString());
console.log(i+++"--------------------------------------------------");
myController.changeCurrentResearch(1);
console.log("Changed current research by index to research of index = 1")
console.log("Expected result: current research is the research of rid = 4 with the name reseted to Current Name");
console.log(myController.toString());