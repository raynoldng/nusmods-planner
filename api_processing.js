/* Test out some processing of API return calls from NUSMods */

// test data
var cs1010 =
{
    "ModuleCode": "CS1010",
    "Timetable": [
        {
            "ClassNo": "1",
            "LessonType": "Sectional Teaching",
            "WeekText": "Every Week",
            "DayText": "Tuesday",
            "StartTime": "1000",
            "EndTime": "1300",
            "Venue": "i3-0345"
        },
        {
            "ClassNo": "1",
            "LessonType": "Tutorial",
            "WeekText": "Every Week",
            "DayText": "Friday",
            "StartTime": "1000",
            "EndTime": "1200",
            "Venue": "COM1-B108"
        },
        {
            "ClassNo": "2",
            "LessonType": "Tutorial",
            "WeekText": "Every Week",
            "DayText": "Friday",
            "StartTime": "1200",
            "EndTime": "1400",
            "Venue": "COM1-B108"
        },
        {
            "ClassNo": "3",
            "LessonType": "Tutorial",
            "WeekText": "Every Week",
            "DayText": "Friday",
            "StartTime": "1400",
            "EndTime": "1600",
            "Venue": "COM1-0120"
        }
    ],
};

// break them into groups according to lesson type
// Sectional Teaching and Tutorial

var lessonTypeSet = new Set();
var cs1010Lessons = cs1010.Timetable;

// iterate thorugh array
for(var i = 0; i < cs1010Lessons.length; i++) {
    lessonTypeSet.add(cs1010Lessons[i].LessonType);
}

console.log(lessonTypeSet);

// filter according to lesson type
var lessonTypeArr = Array.from(lessonTypeSet);

console.log(lessonTypeArr);


