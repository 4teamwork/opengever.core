(function($) {
    function usersAndGroupsTemplate(widget) {
        return function(data) {
            // This template will mark users and groups with an icon. Additionaly
            // it links groups with an overlay to see all group-members.
            if (!data.id) {
                // Happens while searching
                return data.text;
            }

            var isGroup = false;
            var principalId = "";
            var principalTitle = "";
            var baseClass = "keywordWidgetUsersAndGroupsElement";
            var groupMemberEndpoint = "@@list_groupmembers";

            function init(data) {
                var principal = data.id.split("group:");
                if (principal.length > 1) {
                    isGroup = true;
                }
                principalId = principal[principal.length - 1];
                principalTitle = data.text;
            }

            function generateUserElement() {
                var element = $("<span />");
                element.addClass(baseClass);
                element.append($("<span class='fa fa-user'></span>"));
                element.append($("<span />").text(principalTitle));
                return element;
            }

            function generateGroupElement() {
                var element = $("<a />");
                element.addClass(baseClass);
                element.attr("href", groupMemberEndpoint + "?group=" + principalId);
                element.append($("<span class='fa fa-users'></span>"));
                element.append($("<span />").text(principalTitle));
                element.prepOverlay({
                    subtype: "ajax",
                });

                return element;
            }

            init(data);

            if (isGroup) {
                return generateGroupElement();
            } else {
                return generateUserElement();
            }
        };
    }

    $(document).on("ftwKeywordWidgetInit", function() {
        window.ftwKeywordWidget.registerTemplate("usersAndGroups", usersAndGroupsTemplate);
    });
})(jQuery);
