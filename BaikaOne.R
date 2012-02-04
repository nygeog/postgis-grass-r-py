# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
# Name:
#   baikaOne
# Description:
#   Elliptic Fourier Descripter for shapefile.
# Parameters:
#   harmo: Number of harmonix for elliptic fourier descriptors. Default is 20.
#   poly: Input polygon dataframes.
# Values:
#   Returns elliptic fouier descriptors matrix.
# Example:
#   shp <- readShapePoly("path/to/the/shapefilename.shp")
#   baika(shp,harmo=20)
# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
baikaOne <- function(polys, harmo=20, normalized=TRUE){
    require(sp)
    require(maptools)
    
    # Counts number of polygons
    n <- length(polys)
    
    # Create Prograss Bar.
    pb <- txtProgressBar(min=0,max=n)
    
    # Row labels are acquired from shape IDs.
    nam <- character(n)
    
    # Column names.
    clb <- character(harmo*4)
    
    res <- list()
    res$efds <- list()
    res$matrix <- matrix(numeric(0),n,(harmo*4))
    for (i in seq(1:n)){
        # Update progress bar.
        setTxtProgressBar(pb,i)
        
        # Extracts control points from the polygon object.
        p <- length(polys@polygons[[i]]@Polygons)

        for (j in seq(1:p)){
            if(polys@polygons[[i]]@Polygons[[j]]@hole==FALSE){
                ctrlPts <- polys@polygons[[i]]@Polygons[[j]]@coords
                break()
            }
        }
        
        # Gets Identifier of the polygon
        IDvar <- polys@polygons[[i]]@ID
        nam[i] <- IDvar
        
        # Calculates EFD.
        if (normalized==TRUE){
            res$efds[[i]] <- baika.efd(IDvar, ctrlPts,harmo=harmo,normalized=TRUE)    
        } else {
            res$efds[[i]] <- baika.efd(IDvar, ctrlPts,harmo=harmo,normalized=FALSE)    
        }
        
        # Take a name from the shape ID.
        for (j in seq(1:harmo)){
            # Input each EFD to the matrix.
            k <- j+(j-1)*3
            res$matrix[i,k] <- res$efds[[i]]$descriptors$A[j]
            res$matrix[i,(k+1)] <- res$efds[[i]]$descriptors$B[j]
            res$matrix[i,(k+2)] <- res$efds[[i]]$descriptors$C[j]
            res$matrix[i,(k+3)] <- res$efds[[i]]$descriptors$D[j]
            
            # Make a list of column labels if i is 1.
            if (i==1){
                clb[k] <- paste("A",j,sep="")
                clb[k+1] <- paste("B",j,sep="")
                clb[k+2] <- paste("C",j,sep="")
                clb[k+3] <- paste("D",j,sep="")   
            }
        }
    }
    # Asigns columun and row names to the matrix.
    rownames(res$matrix) <-nam
    colnames(res$matrix) <- clb
    
    # Returns matrix.
    return(invisible(res))
}

# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
# Name:
#   baikaOneinv
# Description:
#   Build approximated polygon from elliptic fourier descriptors.
# Parameters:
#   efds: efds are acquired by baika.
#   approx: Number of points for approximates.
# Values:
#   Returnes SpatialPolygonDataFrame class
# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
baikaOneinv <- function(efds, approx){
    require(sp)
    require(maptools)
    
    # Gets number of polygons
    n <- length(efds$efds)
    polys <- vector("list", n)

    # Creates the Prograss Bar.
    pb <- txtProgressBar(min=0,max=n)
    
    for (i in seq(1:n)){
        # Update progress bar.
        setTxtProgressBar(pb,i)
        
        # Creates Polygon instance form coordinates of the approximated shape.
        poly <- Polygon(baika.reconstruct(efds$efds[i],approx),hole=FALSE)
        
        # Gets ID label from original IDs.
        fid <- as.character(efds$efds[i][[1]]$id)
        
        # Build SpatialPolygon instance from the shape.
        polys[[i]] <- Polygons(list(Polygon(poly)), ID=fid)
    }
    
    # Convert from SpatialPolygon dataframe to SpatialPolygonDataFrame.
    spPoly <- SpatialPolygons(polys)
    ids <- sapply(slot(spPoly, "polygons"), function(x) slot(x, "ID"))
    length(ids)
    df <- data.frame(rep(0,length(ids)), row.names=ids)
    res <- SpatialPolygonsDataFrame(spPoly,df)
    
    # Return SpatialPolygonDataFrame.
    return(invisible(res))
}


# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
# Name:
#   baikaTwo
# Description:
#   Procrustes Analysis for spatial polygon dataframe created by baikaOneInv.
# Parameters:
#   poly: Input polygon dataframes.
# Values:
#   Returns elliptic fouier descriptors matrix.
# Example:
#   shp <- readShapePoly("path/to/the/shapefilename.shp")
#   baika(shp,harmo=20)
# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
baikaTwo <- function(polys){
    require(vegan)
    require(sp)
    require(maptools)
    
    # Counts number of polygons
    n <- length(polys)
    
    # Create Prograss Bar.
    pb <- txtProgressBar(min=0,max=n)
    
    # Row labels are acquired from shape IDs.
    rNams <- character(n)
    cNams <- character(n)
    
    res <- matrix(nrow=n,ncol=n)
    
    for (i in seq(1:n)){
        # Update progress bar.
        setTxtProgressBar(pb,i)
        
        # Extracts control points from the polygon object.
        p <- length(polys@polygons[[i]]@Polygons)

        for (k in seq(1:p)){
            if(polys@polygons[[i]]@Polygons[[k]]@hole==FALSE){
                A <- polys@polygons[[i]]@Polygons[[k]]@coords
                break()
            }
        }
        
        # Gets Identifier of the polygon
        rNams[i] <- polys@polygons[[i]]@ID
        
        for (j in seq(1:n)){
            # Extracts control points from the polygon object.
            p <- length(polys@polygons[[j]]@Polygons)
    
            for (k in seq(1:p)){
                if(polys@polygons[[j]]@Polygons[[k]]@hole==FALSE){
                    B <- polys@polygons[[j]]@Polygons[[k]]@coords
                    break()
                }
            }
            
            # Gets Identifier of the polygon
            if (i==1){
                cNams[j] <- polys@polygons[[j]]@ID   
            }
            res[i,j] <- procrustes(A,B,symmetric=TRUE)$ss
        }
    }
    # Asigns columun and row names to the matrix.
    rownames(res) <- rNams
    colnames(res) <- cNams
    
    # Returns matrix.
    return(invisible(res))
}

# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
# Name:
#   GetEfd
# Description:
#   Elliptic Fourier Descripter for sp polygon dataframe.
# Parameters:
#   harmo: Number of harmonix for elliptic fourier descriptors. Default is 20.
#   poly: Input polygon.
# Example:
#   shp <- readShapePoly("path/to/the/shapefilename.shp")
#   GetEfd(shp@polygons[[3]]),harmo=20)
# _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
baika.efd <- function(IDvar, ctrlPts, harmo=20, normalized=TRUE){
    require(sp)
    require(maptools)
    
    res <- list()
    
    if (harmo<1) {
        #  If harmonix is less than 1 then exit.
        exit()
    }
    
    n <- nrow(ctrlPts)
    ti <- baika.lenFromStart(ctrlPts)
    l <- ti[n]
    
    res$id <- IDvar
    res$NumsOfPoints <- n
    res$totalLength <- l
    res$EdgeLengthFromStart <- ti
    res$centroid <- c(0,0)
    
    res$harmonix <- harmo
    res$parameters <- list()
    res$parameters$theta <- numeric(length=harmo)
    res$parameters$alpha <- numeric(length=harmo)
    res$parameters$beta <- numeric(length=harmo)
    res$parameters$phi <- numeric(length=harmo)
    res$parameters$ee <- numeric(length=harmo)
    
    res$descriptors <- list()
    res$descriptors$IsNormalized <- normalized
    res$descriptors$N <- harmo
    res$descriptors$A <- numeric(length=harmo)
    res$descriptors$B <- numeric(length=harmo)
    res$descriptors$C <- numeric(length=harmo)
    res$descriptors$D <- numeric(length=harmo)
    
    for (i in seq(1:harmo)){ 
        Ai <- 0
        Bi <- 0
        Ci <- 0
        Di <- 0
        
        for (j in seq(1:(n-1))){
            t1 <- ti[j]
            t2 <- ti[j+1]
            
            CosT1 <- cos((2*pi*i*t1)/l)
            CosT2 <- cos((2*pi*i*t2)/l)
            
            SinT1 <- sin((2*pi*i*t1)/l)
            SinT2 <- sin((2*pi*i*t2)/l)
            
            # Calculate Elliptic Fourier Descriptor for F(x)
            thisXi = ctrlPts[j,1]
            NextXi <- ctrlPts[j+1,1]
            
            Ai <- Ai+((CosT2-CosT1)*(((NextXi-thisXi)*l)/(t2-t1)))/(4*(pi^2)*(i^2))
            Bi <- Bi+((SinT2-SinT1)*(((NextXi-thisXi)*l)/(t2-t1)))/(4*(pi^2)*(i^2))
            
            # Calculate Elliptic Fourier Descriptor for G(x)
            thisYi <- ctrlPts[j,2]
            nextYi <- ctrlPts[j+1,2]
            
            Ci <- Ci+((CosT2-CosT1) * (((nextYi-thisYi)*l)/(t2-t1)))/(4*(pi^2)*(i^2))
            Di <- Di+((SinT2-SinT1) * (((nextYi-thisYi)*l)/(t2-t1)))/(4*(pi^2)*(i^2))
        }
        
        if (normalized==TRUE){
            X <- Ai^2+Ci^2-Bi^2-Di^2
            Y <- 2*(Ai*Bi+Ci*Di)
            
            pram_theta <- 0.5*(atan2(Y, X))
            pram_alpha <- Ai*cos(pram_theta)+Bi*sin(pram_theta)
            pram_beta <- Ci*cos(pram_theta)+Di*sin(pram_theta)
            param_phi <- atan2(pram_beta,pram_alpha)
            param_ee <- sqrt(pram_alpha^2+pram_beta^2)
            
            res$parameters$theta[i] <- pram_theta
            res$parameters$alpha[i] <- pram_alpha
            res$parameters$beta[i] <- pram_beta
            res$parameters$phi[i] <- param_phi
            res$parameters$ee[i] <- param_ee
            
            SinTheta <- sin(pram_theta*i)
            CosTheta <- cos(pram_theta*i)
            SinPhi <- sin(param_phi)
            CosPhi <- cos(param_phi)
            
            res$descriptors$A[i]<-((CosPhi*Ai+SinPhi*Ci)*(CosTheta)+(CosPhi*Bi+SinPhi*Di)*SinTheta)/param_ee
            res$descriptors$B[i]<-((CosPhi*Ai+SinPhi*Ci)*(-1*SinTheta)+(CosPhi*Bi+SinPhi*Di)*CosTheta)/param_ee
            res$descriptors$C[i]<-((-1*SinPhi*Ai+CosPhi*Ci)*(CosTheta)+(-1*SinPhi*Bi+CosPhi*Di)*SinTheta)/param_ee
            res$descriptors$D[i]<-((-1*SinPhi*Ai+CosPhi*Ci)*(-1*SinTheta)+(-1*SinPhi*Bi+CosPhi*Di)*CosTheta)/param_ee
        } else {
            res$centroid[1] <- baika.centroid(ctrlPts, IDvar=IDvar)$coord[1]
            res$centroid[2] <- baika.centroid(ctrlPts, IDvar=IDvar)$coord[2]            
            res$descriptors$A[i]<-Ai
            res$descriptors$B[i]<-Bi
            res$descriptors$C[i]<-Ci
            res$descriptors$D[i]<-Di
        }
    }
    return(invisible(res))
}

baika.reconstruct <- function(efd, approx){
    h <- efd[[1]]$harmonix
    res <- matrix(nrow=(approx+1),ncol=2)
    
    A1 <- efd[[1]]$descriptors$A[1]
    B1 <- efd[[1]]$descriptors$B[1]
    C1 <- efd[[1]]$descriptors$C[1]
    D1 <- efd[[1]]$descriptors$D[1]
    
    for (i in seq(1:approx)){
        
        theta <- (i*2*pi)/approx
        sX1 <- A1*cos(theta)+B1*sin(theta)
        sY1 <- C1*cos(theta)+D1*sin(theta)
        
        sXi <- 0
        sYi <- 0

        for (j in seq(2:h)){
            Aj <- efd[[1]]$descriptors$A[j]
            Bj <- efd[[1]]$descriptors$B[j]
            Cj <- efd[[1]]$descriptors$C[j]
            Dj <- efd[[1]]$descriptors$D[j]
            
            sXi = sXi+Aj*cos(j*theta)+Bj*sin(j*theta)
            sYi = sYi+Cj*cos(j*theta)+Dj*sin(j*theta)   
        }
        
        res[i,1] <- sX1+sXi+efd[[1]]$centroid[1]
        res[i,2] <- sY1+sYi+efd[[1]]$centroid[2]
    }
    
    res[(approx+1),1] <- res[1,1]
    res[(approx+1),2] <- res[1,2]
        
    return(invisible(res))
}

baika.lenFromStart <- function(ctrlPts){
    # Count the number of control points.
    n <- nrow(ctrlPts)
    
    # Get the first set of coordinates of the first point.
    sx <- ctrlPts[1,1]
    sy <- ctrlPts[1,2]
    
    res <- {}
    res[1] <- 0
    
    # Get length from start point at each control point.
    for (i in seq(2:n)){
        thisXi <- ctrlPts[i,1]
        thisYi <- ctrlPts[i,2]
        
        nextXi <- ctrlPts[i+1,1]
        nextYi <- ctrlPts[i+1,2]
        
        distX <- thisXi-nextXi
        distY <- thisYi-nextYi
        
        res[i+1] <- res[i]+(sqrt(distX^2+distY^2))
    }
    return(invisible(res))
}

baika.startPoint <- function(ctrlPts, IDvar=1){
    res <- list()
    res$id <- IDvar
    res$coord <- c(0,0)
    
    res$coord[1] <- ctrlPts[1,1]
    res$coord[2] <- ctrlPts[1,2]
    
    return(invisible(res))  
}

baika.centroid <- function(ctrlPts, IDvar=1){
    n <- nrow(ctrlPts)
    ti <- baika.lenFromStart(ctrlPts)
    l <- ti[n]
    
    res <- list()
    res$id <- IDvar
    res$coord <- c(0,0)
    
    for (i in seq(1:(n-1))){

        thisXi <- ctrlPts[i,1]
        thisYi <- ctrlPts[i,2]

        nextXi <- ctrlPts[i+1,1]
        nextYi <- ctrlPts[i+1,2]

        dist <- ti[i+1]-ti[i]
        res$coord[1] <- res$coord[1]+((nextXi+thisXi)/2*(dist))
        res$coord[2] <- res$coord[2]+((nextYi+thisYi)/2*(dist))

    }
        
    res$coord[1] <- res$coord[1]/l
    res$coord[2] <- res$coord[2]/l
    
    return(invisible(res))   
}
    
baika.area <- function(efds){
    res <- 0
    n <- length(efds$A[i])
    for (i in seq(1:n)){
        Ai <- efds$A[i]
        Bi <- efds$B[i]
        Ci <- efds$C[i]
        Di <- efds$D[i]
        res <- res+((Ai*Di)-(Ci*Bi))*i*pi
    }
    return(invisible(res))
}