/**
 * Created by jdbiskner on 10/16/2017.
 */

var marked_pairs = {match_type: "" , pairs: []};

var yes_count = 0;

var no_count = 0;

$(function() {

    // Remove the intro text and replicate it with the new text.
    $("#begin_training").click(function(){
        startTrainer();
    });

    // yes button behavior
    $("#markPairYes").click(function(){
        markPairs("match");

        // update the progress bar
        yes_count += 1;
        var style_string = "width: " + yes_count + "0%;";
        $("#yesProgress").attr("style", style_string);

        if((yes_count >= 10 && no_count >= 10) || no_count >= 75) {
            $("#markFinish").prop("disabled", false);
        }

        // update the count in the ui
        $("#matchesLabelCount").html(yes_count + ' / 10');

    });

    // no button behavior
    $("#markPairNo").click(function(){
        markPairs("distinct");

        // update the progress bar
        no_count += 1;
        var style_string = "width: " + no_count + "0%;";
        $("#noProgress").attr("style", style_string);

        if((yes_count >= 10 && no_count >= 10) || no_count >= 75) {
            $("#markFinish").prop("disabled", false);
        }

        // update the count in the ui
        $("#distinctLabelCount").html(no_count + ' / 10');

    });

    // unsure button behavior
    $("#markPairUnsure").click(function(){
        uncertainPairs();
    });

});

/**
 * Begins the trainer
 */
function startTrainer(callback) {

    // get a pair of records for comparison
    uncertainPairs(function(){
        $("#trainer_info").remove();
        $(".trainer").show();
    });
}
/**
 * Gets a set of uncertain pairs from the server and load them into the interface
 */
function uncertainPairs(callback) {

    // initialize content to display
    var contentstring = '';

    var counter = 0;

    // grab uncertain pairs
    $.getJSON(Flask.url_for("uncertain_pairs"))
        .done(function(data, textStatus, jqXHR) {

            // store data for later usuage
            marked_pairs.pairs = JSON.parse(JSON.stringify(data));

            // TODO There's the possibility this can be improved given what I know about JSON now
            $.each(data, function(i, pair) {

                // structure the column by accessing the pair
                $.each(pair, function(label, obj) {
                    contentstring += '<b>' + label + ': </b>' + obj + '</b> <br><br>';

                });

                // create a selector using the loop in order to access the right column.
                var selector_string = '#pair_record_' + counter;

                // update the inner html of the column panel
                $(selector_string).html(contentstring);

                // prepare variables for the next loop
                contentstring = '';
                counter++;
            });

            // run the callback

            if (callback !== undefined) {
                callback();
            }

        })
        .fail(function(jqXHR, textStatus, errorThrown) {

            // log error to browser's console
            console.log(errorThrown.toString());
        });
}

/**
 * Marks the pairs shown in the UI
 */
function markPairs(mark_value) {

    marked_pairs.match_type = mark_value;

    $.ajax({
        type: 'POST',
        url: Flask.url_for("markpairs"),
        data: JSON.stringify(marked_pairs),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    }).success(function (data, textStatus, jqXHR) {
        uncertainPairs();
    });
}