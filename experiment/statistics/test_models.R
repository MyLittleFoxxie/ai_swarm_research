# Run from experiment/: Rscript statistics/test_models.R
source("statistics/models.R")
source("statistics/design.R")
set.seed(12345)
for(h in paste0("H",1:6)) {
  baseline<-if(h=="H6") 5 else if(h=="H5") .01 else .5
  effect<-if(h=="H6") 1.25 else if(h=="H5") .005 else .1
  d<-simulate_design(h,5,baseline,.1,effect)
  stopifnot(all(d$y>=0))
  if(h=="H5") {
    # Every winner ends their run: total winners per run cannot exceed 3.
    stopifnot(all(tapply(d$y,d$run_id,sum)<=3), all(d$y %in% 0:1))
  }
  result<-tryCatch(primary_contrast(h,fit_primary(h,d)),error=function(e) NULL)
  if(h!="H5") stopifnot(!is.null(result))
  if(!is.null(result)) stopifnot(is.finite(result$p),result$p>=0,result$p<=1,result$se>0)
  # Fitting failure is allowed but never silently replaced with a simpler model.
}
d<-simulate_design("H4",5,.5,.1,.1);d$y<-0
failed<-tryCatch({fit_primary("H4",d);FALSE},error=function(e) TRUE)
stopifnot(failed)
stopifnot(inherits(try(simulate_design("H5",5,.01,.1,.1),silent=TRUE),"try-error"))
cat("Statistical generator/contrast and failure-path checks passed.\n")
