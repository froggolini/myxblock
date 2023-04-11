/* Javascript for MyXBlock. */
function MyXBlock(runtime, element) {
    var imageName = ""
    
    function updateLink(result) {
        var selectedOption = $('#selector').find(':selected')[0].value;
        console.log(selectedOption)
        $('.placeholderXss').toggle(selectedOption === 'xss');
        $('.placeholderSqli').toggle(selectedOption === 'sqli');
        $(".create-lab").attr("disabled", true);
        $('.iframe', element).attr('src', result.container);

        if (selectedOption === "sqli") {
            $("#webAccess a").prop("href", result.web_url) 
            $("#phpAccess a").prop("href", result.php_url) 
            $("#sshAccess a").text(result.ssh_ip)
            $("#dbAccess a").text(result.db_ip) 
        } else if (selectedOption === "xss") {
            $("#webAccess a").prop("href", result.web_url) 
        }
        
    }

    function resetLink() {
        var selectedOption = $('#selector').find(':selected')[0].value;
    
        $('.iframe', element).attr('src', "about:blank");
        $("#webAccess a").prop("href", "") 
        $("#phpAccess a").prop("href", "") 
        $("#dbAccess a").prop("href", "") 

        $("#myElem").show(1000);
        $(".create-lab").attr("disabled", false);
        $('.placeholderXss').hide(selectedOption === 'xss');
        $('.placeholderSqli').hide(selectedOption === 'sqli');
        $("#myElem").hide(5000);
        $('#time').toggle();
     
    }
    

    var handlerStartUrl = runtime.handlerUrl(element, 'create_container');
    
    $('.create-lab', element).click(function(eventObject) {
        imageName = getImageName();
        $.ajax({
            type: "POST",
            url: handlerStartUrl,
            data: JSON.stringify({"imageName": imageName}),
            success: updateLink
        });
        started = true
        setTimeout(function() {
            var imageName = getImageName();
            $.ajax({
              type: "POST",
              url: handlerStopUrl,
              data: JSON.stringify({"imageName": imageName}),
              success: resetLink
            });
          }, 300000);
    });

    function getImageName() {
        var selectedOption = $('#selector').find(':selected')[0].value;

        if (selectedOption === "sqli") {
          imageName = "sqli";
        } else if (selectedOption === "xss") {
          imageName = "xss";
        }
      
        return imageName;
      }

    var handlerStopUrl = runtime.handlerUrl(element, 'stop_container');

    $('.stop-lab', element).click(function(eventObject) {
        var imageName = getImageName();
        $.ajax({
            type: "POST",
            url: handlerStopUrl,
            data: JSON.stringify({"imageName": imageName}),
            success: resetLink
        });
    });


    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
