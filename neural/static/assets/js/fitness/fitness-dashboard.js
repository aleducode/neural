/*! investment dashboard.js | Adminuiux 2023-2024 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {
    /* chart js areachart summary  */
    window.randomScalingFactor = function () {
        return Math.round(Math.random() * 20);
    }

    /* summary chart */
    var lineheartchart = document.getElementById('lineheart').getContext('2d');
    var gradient2 = lineheartchart.createLinearGradient(0, 0, 0, 100);
    gradient2.addColorStop(0, 'rgba(0, 200, 10, 0.25)');
    gradient2.addColorStop(1, 'rgba(0, 200, 117, 0)');

    var lineheartConfig = {
        type: 'line',
        data: {
            labels: ['10:30', '11:00', '11:30', '12:00', '12:30', '01:00', '01:30'],
            datasets: [{
                label: '# of hours',
                data: [
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                    randomScalingFactor(),
                ],
                radius: 0,
                backgroundColor: gradient2,
                borderColor: '#28a745',
                borderWidth: 1,
                fill: true,
                tension: 0.0,
            }]
        },
        options: {
            animation: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                y: {
                    display: false,
                    beginAtZero: true,
                },
                x: {
                    grid: {
                        display: false
                    },
                    display: false,
                    beginAtZero: true,
                }
            }
        }
    }
    var lineheart = new Chart(lineheartchart, lineheartConfig);
    /* my area chart randomize */
    setInterval(function () {
        lineheartConfig.data.datasets.forEach(function (dataset) {
            dataset.data = dataset.data.map(function () {
                return randomScalingFactor();
            });
        });
        lineheart.update();
    }, 3000);

    /* circular progress */
    /* green circular progress */
    var progressCirclesgreen2 = new ProgressBar.Circle(circleprogressgreen2, {
        color: 'rgba(8, 160, 70, 1)',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 5,
        trailWidth: 10,
        easing: 'easeInOut',
        trailColor: 'rgba(8, 160, 70, 0.15)',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: { color: 'rgba(8, 160, 70, 0)', width: 5 },
        to: { color: 'rgba(8, 160, 70, 1)', width: 5 },
        // Set default step function for all animate calls
        step: function (state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);
        }
    });
    // progressCirclesgreen2.text.style.fontSize = '20px';
    progressCirclesgreen2.animate(0.70);  // Number from 0.0 to 1.0


    /* orange progress */
    var progressCirclesorange1 = new ProgressBar.Circle(circleprogressorange1, {
        color: 'rgba(252, 122, 30, 1)',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 8,
        trailWidth: 2,
        easing: 'easeInOut',
        trailColor: 'rgba(252, 122, 30, 0.15)',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: { color: 'rgba(252, 122, 30, 0)', width: 8 },
        to: { color: 'rgba(252, 122, 30, 1)', width: 8 },
        // Set default step function for all animate calls
        step: function (state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);
        }
    });
    // progressCirclesgreen1.text.style.fontSize = '20px';
    progressCirclesorange1.animate(0.65);  // Number from 0.0 to 1.0

})
