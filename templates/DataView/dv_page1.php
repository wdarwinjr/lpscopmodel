{% load static %}

<!DOCTYPE HTML>
<html lang="pt-br">
	<head>
		<meta charset="UTF-8">

		<title>User Home</title>
		
		<!-- jquery - link cdn -->
		<script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>

		<!-- bootstrap - link cdn -->
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
	
		<link rel="stylesheet" type="text/css" href="{% static 'uspdarwin_app/css/wd-style.css' %}">
		<!--<link rel="stylesheet" type="text/css" href="{% static 'uspdarwin_app/style.css' %}">-->
	
	</head>


	<body style="background-color: #EEE;">

		{% include 'std.php' %}

    	<div class="col-md-12">DATA MODELING USING COPULA</div>

	    <div class="container">
	    	<div>PAGE1</div>
	    	<form action="page2.php"  method="get"><!--onsubmit="return false;"-->
		    	<div>
		    		<h5 style="margin-top:40px;">Filter Selection</h5>
		    		<!--<div name="filter_txt" id="filter_txt" style=" background-color: #FFF;border-style:solid; border-width:1px; margin:0px; padding:5px; height:80px; overflow-y:scroll;">-->
		    			<input type="text" name="filter_text" value="" style="background-color:#FFF; border-style:solid; border-width:1px; margin:0px; padding:5px; height:80px; overflow-y:scroll;">
		    		<!--</div>-->
					<input type="submit" value="Submit" align="center">
		    	</div>
	    	</form>
	    	<div class="col-md-4">XXX</div>
	    	<div class="col-md-4">
				<figure>
				  <img src="{% static 'usp-darwin_app/images/background.png' %}" alt="Minha Figura">	
				  <figcaption>Informações da Figura</figcaption>
				</figure>
			</div>
	    	<div class="col-md-4"></div>
	    </div>

		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
	
	</body>
</html>