/**
 * Configures application.
 */
// configure typeahead
// A $( document ).ready() block.
$( document ).ready(function() {
    
    // configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div><a href='https://ide50-md2252.cs50.io/itm/{{item_id}}'> {{ item_name }} </a></div>"
            )
        }
    });

    
    
});

/**
 * Searches database for typeahead's suggestions.
 */
function search(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("search"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
        
        console.log(data)
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}


/*
** Validate Form
*/


function validateLogin() {

    // Validate username
    var username = $("#frusername").val();
    if (username == "" || username == null) {
        alert("Please enter your username");
        return false;
    }
    
    // Validate Email
    var password = $("#frpassword").val();
    if ( password == "" || password == null) {
        alert("Please enter a valid password");
        return false;
    }
    
  return true;
}

function validateRegister() {

    // Validate username
    var username = $("#frusername").val();
    if (username == "" || username == null) {
        alert("Please enter your username");
        return false;
    }
    // Validate email
    var email = $("#fremail").val();
    if ( email == "" || email == null ) {
        alert("Please enter a valid email");
        return false;
    }
    
    // Validate Email
    var password = $("#frpassword").val();
    if ( password == "" || password == null) {
        alert("Please enter a valid password");
        return false;
    }
    
  return true;
}


function validateSell(){
    
    var name = $("#frname").val();
    if ( name == "" || name == null) {
        alert("Please enter a valid name");
        return false;
    }
        
    var description = $("#frdescription").val();
    if ( description == "" || description == null) {
        alert("Please enter a valid description");
        return false;
    }
    
    var bid = $("#fr1bid").val();
    if ( bid == "" || bid == null) {
        alert("Please enter a valid bid");
        return false;
    }
}